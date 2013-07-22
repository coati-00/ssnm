# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "tgdev"
  config.vm.box_url = "http://slank.ccnmtl.columbia.edu/tgdev.box"
  config.vm.network :forwarded_port, guest: 8000, host: 5556
end
