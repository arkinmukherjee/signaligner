VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.hostname = "signaligner"

  config.vm.network :forwarded_port, guest: 3007, host: 3007, auto_correct: true

  config.vm.provision "shell", inline: <<-SHELL
    apt install -y python
  SHELL
end
