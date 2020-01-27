import requests
import os, re, sys, json, multiprocessing
import _root
import _folder, _helper
sys.path.append(_root.root_abspath('mdcas-python'))


# UI size constants
BUTTON_WIDTH = 15
DROPDOWN_ALGO_WIDTH = 8
DROPDOWN_DATASET_WIDTH = 50
NO_DATASET_WIDTH = 53
should_continue = True


# determine data folder
if getattr(sys, 'frozen', False):
    _folder.file_folder = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'signaligner'))
_folder.data_folder = os.path.abspath(os.path.join(os.path.expanduser("~"), 'Documents', 'SignalignerData'))



# set up logging to files
class Logger:
    def __init__(self, stream1, stream2):
        self.stream1 = stream1
        self.stream2 = stream2

    def write(self, data):
        self.stream1.write(data)
        self.stream2.write(data)

    def flush(self):
        self.stream1.flush()
        self.stream2.flush()

logfilename = _folder.data_abspath('log', 'signalauncher.' + str(os.getpid()) + '.txt')
logfile = open(_helper.ensureDirExists(logfilename, True), 'wt')
sys.stdout = Logger(sys.stdout, logfile)
sys.stderr = Logger(sys.stderr, logfile)


# utility functions
def datasetexists(dataset):
    out_folder = _helper.datasetDir(dataset)
    return os.path.exists(out_folder)

def mhealthfolder(dataset, signal):
    return _folder.data_abspath('algo', dataset, 'mhealth', signal)

def algofolder(dataset, signal):
    return _folder.data_abspath('algo', dataset, 'output', signal)

def get_dataset_raw_file_paths(dataset):
    origin_file = _helper.datasetOriginFilename(dataset)
    if os.path.exists(origin_file):
        with open(origin_file, 'rt') as origin:
            origin_json = json.load(origin)
            return origin_json['origin']
    return ['ERROR']



# import UI elements
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog



class Signalauncher(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.datasetSelected = None
        self.algorithmSelected = None
        self.algorithmCSVSelected = None
        self.algorithmCSVSelectedPath = None
        self.copyLabelsFromDataset = None
        self.processes = []
        self.server_pid = 0
        self.create_widgets()
        
    def close_window(self):
        for process in self.processes:
            process.terminate()
        self.master.withdraw()
        self.master.update()
        self.master.destroy()

    def update_select_dataset_widget(self, datasets):
        if len(datasets) > 0:
            self.datasetSelected = tk.StringVar(self)
            self.datasetSelected.set(datasets[0])
            dataset_dropdown = tk.OptionMenu(self, self.datasetSelected, *datasets, command=self.handle_select_dataset)
            dataset_dropdown.config(width=DROPDOWN_DATASET_WIDTH)
            dataset_dropdown.grid(row=4, column=1, sticky="w")
        else:
            box = tk.OptionMenu(self, "None", 0, command=self.handle_select_dataset)
            box.config(width=DROPDOWN_DATASET_WIDTH)
            box.grid(row=4, column=1, sticky="w")
            box.config(state="disabled")
            dataset_label = tk.Label(self, text="Please import a dataset first",anchor='w')
            dataset_label.grid(row=4, column=1, sticky="w")
            dataset_label.config(width=NO_DATASET_WIDTH)

    def update_copy_labels_widget(self, datasets):
        if len(datasets) > 0:
            self.copyLabelsFromDataset = tk.StringVar(self)
            self.copyLabelsFromDataset.set(datasets[0])

            copy_labels_from_dropdown = tk.OptionMenu(self, self.copyLabelsFromDataset, *datasets)
            copy_labels_from_dropdown.config(width=DROPDOWN_DATASET_WIDTH)
            copy_labels_from_dropdown.grid(row=10, column=1, sticky="w")

            tk.Button(self, text="Copy", command=self.handle_copy_labels, width=BUTTON_WIDTH).grid(row=10, column=2, columnspan=2, sticky="w")

        else:
            box = tk.OptionMenu(self, "None", 0, command=self.handle_select_dataset)
            box.config(width=DROPDOWN_DATASET_WIDTH)
            box.grid(row=10, column=1, sticky="w")
            box.config(state="disabled")
            copy_label = tk.Label(self, text="Please import a dataset first",anchor='w')
            copy_label.grid(row=10, column=1, columnspan=3, sticky="w")
            copy_label.config(width=NO_DATASET_WIDTH)


    def create_widgets(self):
        self.server_button = tk.Button(self)

        tk.Label(self, text='Open Test Dataset:').grid(row=0, column=0, sticky="w")
        tk.Button(self, text='Open', command=self.handle_opentest, width=BUTTON_WIDTH).grid(row=0, column=1, sticky="w")

        tk.Label(self, text='Import Single Dataset:').grid(row=1, column=0, sticky="w")
        tk.Button(self, text='Select File/Folder', command=self.handle_import_dataset, width=BUTTON_WIDTH).grid(row=1, column=1, sticky="w")

        tk.Label(self, text='Import Multiple Datasets:').grid(row=2, column=0, sticky="w")
        tk.Button(self, text='Select Folder', command=self.handle_import_all_dataset, width=BUTTON_WIDTH).grid(row=2, column=1, sticky="w")

        tk.Label(self, text="").grid(row=3, sticky="w")

        tk.Label(self, text='Select Dataset:').grid(row=4, column=0, sticky="w")

        datasets = _helper.getDatasetList()
        self.update_select_dataset_widget(datasets)

        tk.Label(self, text='Open Selected Dataset:').grid(row=5, column=0, sticky="w")
        tk.Button(self, text="Open", command=self.handle_load_dataset, width=BUTTON_WIDTH).grid(row=5, column=1, sticky="w")

        tk.Label(self, text="Delete Selected Dataset:").grid(row=6, column=0, sticky="w")
        tk.Button(self, text="Delete", command=self.handle_delete_dataset, width=BUTTON_WIDTH).grid(row=6, column=1, sticky="w")

        tk.Label(self, text='Import Dataset Labels:').grid(row=7, column=0, sticky="w")
        tk.Button(self, text='Select File', command=self.handle_import_labels, width=BUTTON_WIDTH).grid(row=7, column=1, sticky="w")

        tk.Label(self, text='Export Dataset Labels:').grid(row=8, column=0, sticky="w")
        tk.Button(self, text="Export", command=self.handle_export_labels, width=BUTTON_WIDTH).grid(row=8, column=1, sticky="w")

        algorithms = ['MUSS', 'SWaN', 'QC']
        self.algorithmSelected = tk.StringVar(self)
        self.algorithmSelected.set(algorithms[0])
        tk.Label(self, text="Run Algorithm on Signal:").grid(row=9, column=0, sticky="w")
        algo_dropdown = tk.OptionMenu(self, self.algorithmSelected, *algorithms)
        algo_dropdown.config(width=DROPDOWN_ALGO_WIDTH)
        algo_dropdown.grid(row=9, column=2, sticky="w")
        self.update_algo_dropdown(None if self.datasetSelected is None else self.datasetSelected.get())
        tk.Button(self, text="Run", command=self.handle_run_algo, width=BUTTON_WIDTH).grid(row=9, column=3, sticky="w")

        tk.Label(self, text="Copy Labels From:").grid(row=10, column=0, sticky="w")
        self.update_copy_labels_widget(datasets)

        tk.Label(self, text="").grid(row=11, sticky="w")

        tk.Label(self, text="Quit Signalauncher:").grid(row=12, column=0, sticky="w")
        tk.Button(self, text="Quit", command=self.handle_quit, width=BUTTON_WIDTH).grid(row=12, column=1, sticky="w")

        tk.Label(self, text="Data In:").grid(row=13, column=0, sticky="w")
        tk.Label(self, text=_folder.data_folder).grid(row=13, column=1, columnspan=3, sticky="w")

        tk.Label(self, text="Log File:").grid(row=14, column=0, sticky="w")
        tk.Label(self, text=logfilename).grid(row=14, column=1, columnspan=3, sticky="w")

    def handle_startserver(self):
        print('Starting server.')

        import signaserver
        p = multiprocessing.Process(target=signaserver.main)
        self.processes.append(p)
        p.start()
        self.server_pid = p.pid

    def handle_stopserver(self):
        if not self.server_pid:
            tk.messagebox.showinfo("Error", "Server is not running!")
            return

        print('Stopping server.')

        for process in self.processes:
            if process.pid == self.server_pid:
                process.terminate()
        self.server_pid = 0

    def handle_opentest(self):
        import webbrowser
        webbrowser.open('http://localhost:3007/signaligner.html?session=DEFAULT')

    def handle_select_dataset(self, event):
        selected_dataset = event
        datasets = _helper.getDatasetList()

        # Update Copy From dataset dropdown list
        self.copyLabelsFromDataset.set(selected_dataset)
        copy_labels_from_dropdown = tk.OptionMenu(self, self.copyLabelsFromDataset, *datasets)
        copy_labels_from_dropdown.config(width=DROPDOWN_DATASET_WIDTH)
        copy_labels_from_dropdown.grid(row=10, column=1, sticky="w")

        # Update algo csv dropdown list
        self.update_algo_dropdown(selected_dataset)

    def update_algo_dropdown(self, dataset):
        # If no datasets are imported yet
        if dataset is None:
            tk.Label(self, text="Please import a dataset first").grid(row=9, column=1, sticky="w")
        else:
            raw_file_paths = get_dataset_raw_file_paths(dataset)
            signal_names = []
            for filename in raw_file_paths:
                signal_names.append(_helper.makeIdFromFilename(filename))
            if len(raw_file_paths) > 1:
                signal_names.append("ALL")
            self.algorithmCSVSelected = tk.StringVar(self)
            self.algorithmCSVSelected.set(signal_names[0])
            datasets = _helper.getDatasetList()
            if len(datasets) > 0:
                algorithm_csv_dropdown = tk.OptionMenu(self, self.algorithmCSVSelected, *signal_names)
                algorithm_csv_dropdown.config(width=DROPDOWN_DATASET_WIDTH)
                algorithm_csv_dropdown.grid(row=9, column=1, sticky="w")
            else: 
                box = tk.OptionMenu(self, "None", 0, command=self.handle_select_dataset)
                box.config(width=DROPDOWN_DATASET_WIDTH)
                box.grid(row=9, column=1, sticky="w")
                box.config(state="disabled")
                algo_label = tk.Label(self, text="Please import a dataset first", anchor='w')
                algo_label.grid(row=9, column=1, sticky="w")
                algo_label.config(width=NO_DATASET_WIDTH)

    def select_raw_data(self, multi_signal=False):
        self.master.withdraw()
        self.master.update()

        data_path = filedialog.askdirectory() if multi_signal else filedialog.askopenfilename()

        self.close_window()

        if data_path != '':
            dataset = _helper.makeIdFromFilename(data_path)
            return data_path, dataset, datasetexists(dataset)
        else:
            return None, None, None

    def handle_import_dataset(self):
        msgBox = tk.messagebox.askyesnocancel("Import Dataset", "Does your dataset contain multiple signals?")
        if msgBox is None:
            return
        else:
            path, dataset, datasetex = self.select_raw_data(msgBox)

            # get list of files to import
            files_to_import = []
            if not msgBox:
                files_to_import.append(path)
            else:
                folder_contents = os.listdir(path)
                csv_files = [os.path.join(path, item) for item in folder_contents if item.endswith(".csv")]
                files_to_import += csv_files

            # import and load dataset
            if path is not None:
                if not datasetex:
                    labelfilenames = [_folder.file_abspath('common', labelfile) for labelfile in ['labels_SWaN.csv', 'labels_MUSS.csv', 'labels_ambsed.csv', 'labels_goodbad.csv', 'labels_unknown.csv']]
                    import import_dataset
                    import_dataset.main(files_to_import, name=dataset, labelfilenames=labelfilenames)
                else:
                    print('dataset %s already imported' % dataset)
                #import webbrowser
                #webbrowser.open('http://localhost:3007/signaligner.html?session=DEFAULT&dataset=' + dataset)

    def handle_import_all_dataset(self):
        #Handle multiple datasets.
        data_path = filedialog.askdirectory()
        print(data_path)
        if data_path is not None:
            try:
                import import_all_datasets
                import_all_datasets.main(data_path)
            except:
                print('An error occured with processing the folder')

    def handle_delete_dataset(self):
        # checks if there is anything to be removed
        if len(_helper.getDatasetList()) == 0:
            tk.messagebox.showerror("Delete Dataset", "There is nothing to be remmoved")
        else:
            msgBox = tk.messagebox.askyesnocancel("Delete Dataset", "Would you also like to delete all files related to the dataset?")
            if msgBox is None:
                return
            else:
                dataset = self.datasetSelected.get()
                import delete_dataset
                delete_dataset.main(dataset, allfiles=msgBox)
                datasets = _helper.getDatasetList()
                self.update_select_dataset_widget(datasets)
                self.update_copy_labels_widget(datasets)
                self.update_algo_dropdown(dataset)

    def handle_load_dataset(self):
        if (self.datasetSelected != None):
            dataset = self.datasetSelected.get() 
        else: 
            tk.messagebox.showerror("Error", "Please import a dataset first!")
            return

        if (dataset != "Select Dataset"):
            import webbrowser
            webbrowser.open('http://localhost:3007/signaligner.html?session=DEFAULT&dataset=' + dataset)
        else:
            messagebox.showwarning("Warning","No dataset has been selected.")

    def handle_import_labels(self):
        dataset = self.datasetSelected.get()
        import_file_path = filedialog.askopenfilename()
        filename = import_file_path
        if import_file_path == '':
            return
        elif not filename.endswith(".csv"):
            tk.messagebox.showerror("Error", "Invalid file format. Please select a csv file to import labels.")
        else:
            import import_labels
            import_labels.main(dataset, import_file_path)

    def handle_export_labels(self):
        dataset = self.datasetSelected.get()
        import export_labels
        export_labels.main(dataset)

    def handle_copy_labels(self):
        from_dataset = self.copyLabelsFromDataset.get()
        to_dataset = self.datasetSelected.get()

        if from_dataset == to_dataset:
            tk.messagebox.showerror("Copy Labels", "The dataset to copy from must not be the selected dataset.")
            return
        else:
            trim = tk.messagebox.askyesnocancel("Copy Labels", "Trim the labels to the length of the selected dataset?")
            if trim is None:
                return
            else:
                import copy_labels
                copy_labels.main(from_dataset, to_dataset, notrim=not trim)

    def handle_run_algo(self):
        if self.datasetSelected is None:
            tk.messagebox.showerror("Alert", "Please import a dataset first.")
            return

        import import_mhealth
        import main
        import import_labels

        algorithm = self.algorithmSelected.get()
        swan = algorithm == 'SWaN'
        muss = algorithm == 'MUSS'
        qc = algorithm == 'QC'

        dataset = self.datasetSelected.get()
        dataset_raw_csv_paths = get_dataset_raw_file_paths(dataset)

        csv_selected = self.algorithmCSVSelected.get()
        run_algo_csv_list = []
        missing_files = []

        for filepath in dataset_raw_csv_paths:
            if csv_selected == "ALL" or _helper.makeIdFromFilename(filepath) == csv_selected:
                run_algo_csv_list.append(filepath)

        for filepath in run_algo_csv_list:
            if not os.path.exists(filepath):
                missing_files.append(filepath)
            else:
                signal_name = _helper.makeIdFromFilename(filepath)
                mhealth_folder = mhealthfolder(dataset, signal_name)
                algo_folder = algofolder(dataset, signal_name)
                if not os.path.exists(mhealth_folder):
                    import_mhealth.main(filepath, mhealth_folder)

                old_cwd = os.path.abspath(os.path.realpath(os.getcwd()))
                os.chdir(_folder.file_abspath('mdcas-python'))
                main.main(mhealth_folder + '/default/', algo_folder + '/default/', 80, profiling=False, swan=swan, muss=muss, qc=qc)
                os.chdir(old_cwd)

                if swan:
                    print("Running SWaN algorithm...")
                    import_labels.main(dataset, algo_folder + '/default/SWaN_output.csv', source='Algo', session='SWaN_' + signal_name)
                elif muss:
                    print("Running MUSS algorithm...")
                    import_labels.main(dataset, algo_folder + '/default/muss_output.csv', source='Algo', session='MUSS_' + signal_name)
                elif qc:
                    print("Running QC algorithm...")
                    import_labels.main(dataset, algo_folder + '/default/qc_output.csv', source='Algo', session='QC_' + signal_name, qcfix=True)

        if len(run_algo_csv_list) > 0:
            tk.messagebox.showinfo("Run Algorithm", "Algorithm labels successfully added for the following files: " +
                                   ", ".join([_helper.makeIdFromFilename(file) for file in run_algo_csv_list]))

        if len(missing_files) > 0:
            tk.messagebox.showerror("Run Algorithm", "The algorithm was not run on the following missing files. Please"
                                                     "move the files back to their locations from when the dataset was"
                                                     "imported: " + ", ".join(missing_files))

    def handle_quit(self):
        global should_continue
        should_continue = False
        self.handle_stopserver()
        self.close_window()

if __name__ == "__main__":
    while should_continue:
        try:
            r=requests.get("http://localhost:3007")
        except OSError:
            r="error"
        if not isinstance(r, requests.models.Response):
            root = tk.Tk()
            root.title("Signalauncher")
            root.resizable(0,0)
            app = Signalauncher(master=root)
            root.protocol("WM_DELETE_WINDOW", app.handle_quit) # add event handler for window close
            app.handle_startserver()
        else:
            tk.Tk().withdraw()
            messagebox.showerror("Error", "There is a server running already!")
            break
        app.mainloop()