#!/bin/bash

echo "FastFLX1 is an easy way to add some cool workarounds and features to your FLX1 device"

	# Update and upgrade the system
	sudo apt update && sudo apt upgrade -y --allow-downgrades
	sudo apt update && sudo apt upgrade -y --allow-downgrades

	# Install required packages
	sudo apt install -y wtype yad

	# Create necessary directories
	mkdir -p "${HOME}/.config/autostart/" "${HOME}/.local/share/applications/"
	sudo mkdir -p /opt/fastflx1/{scripts,configs,share,files}

	# Create symbolic links for the scripts and directories
	sudo ln -sf "${PWD}" "/opt/fastflx1"
	sudo ln -sf "${PWD}/scripts" "/opt/fastflx1/scripts"
	sudo ln -sf "${PWD}/configs" "/opt/fastflx1/configs"
	sudo ln -sf "${PWD}/share" "/opt/fastflx1/share"
	sudo ln -sf "${PWD}/files" "/opt/fastflx1/files"
	sudo ln -sf "${PWD}/install.sh" "/opt/fastflx1/install.sh"
	sudo ln -sf "${PWD}/uninstall.sh" "/opt/fastflx1/uninstall.sh"
	sudo ln -sf "${PWD}/update.sh" "/opt/fastflx1/update.sh"
	sudo ln -sf "${PWD}/README.md" "/opt/fastflx1/README.md"

	# Ensure the scripts are executable
	sudo chmod +x "${PWD}/uninstall.sh" "${PWD}/update.sh"

	# Apply chmod +x for all scripts in the "scripts" folder
	sudo chmod + x "${PWD}/scripts/alarmvol" "${PWD}/scripts/dialtone" "${PWD}/scripts/double-press" "${PWD}/scripts/fastflx1" "${PWD}/scripts/gnome-weather-location" "${PWD}/scripts/long-press" "${PWD}/scripts/short-press" "${PWD}/scripts/squeekboard-scale" 

	    # Apply chmod +x to symlink targets for uninstall/update scripts
	sudo chmod +x "/opt/fastflx1/uninstall.sh" "/opt/fastflx1/update.sh"

	    # Apply chmod +x to all symlinked scripts in /opt/fastflx1/scripts
	sudo chmod + x "/opt/fastflx1/scripts/alarmvol" "/opt/fastflx1/scripts/dialtone" "/opt/fastflx1/scripts/double-press" "/opt/fastflx1/scripts/fastflx1" "/opt/fastflx1/scripts/gnome-weather-location" "/opt/fastflx1/scripts/long-press" "/opt/fastflx1/scripts/short-press" "/opt/fastflx1/scripts/squeekboard-scale" 

	# Move config folders to the user's .config directory
	cp -r ${PWD}/configs/assistant-button ${HOME}/.config/
	cp -r ${PWD}/configs/autostart ${HOME}/.config/
	cp -r ${PWD}/configs/feedbackd-button ${HOME}/.config/
	cp -r ${PWD}/configs/gtk-3.0-button ${HOME}/.config/
	# Move local folders to the local directory
	cp -r ${PWD}/share/keyboards ${HOME}/.local/share/
	cp -r ${PWD}/share/sounds ${HOME}/.local/share/




		# Create desktop entries
		ln -sf "${PWD}/files/fastflx1.desktop" "${HOME}/.local/share/applications/fastflx1.desktop"
		ln -sf "${PWD}/files/yad-icon-browser.desktop" "${HOME}/.local/share/applications/yad-icon-browser.desktop"
		ln -sf "${PWD}/configs/alarmvol.desktop" "${HOME}/.config/autostart/alarmvol.desktop"
		ln -sf "${PWD}/configs/dialtone.desktop" "${HOME}/.config/autostart/dialtone.desktop"

		# Add FastFLX1 paths to the system's PATH
		grep -qxF 'export PATH=$PATH:/opt/fastflx1' ~/.bashrc || echo 'export PATH=$PATH:/opt/fastflx1' >> ~/.bashrc
		grep -qxF 'export PATH=$PATH:/opt/fastflx1/scripts' ~/.bashrc || echo 'export PATH=$PATH:/opt/fastflx1/scripts' >> ~/.bashrc

		# Reload bashrc to apply changes
		source ~/.bashrc


		# Set custom sound theme
		gsettings set org.gnome.desktop.sound theme-name __custom

echo "FastFLX1 setup complete"