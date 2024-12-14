#!/bin/bash

rm ~/.local/share/applications/fastdial.desktop
rm ~/.local/share/applications/yad-icon-browser.desktop
rm ~/.config/autostart/fasthistory.desktop
rm ~/.config/gtk-3.0/gtk.css
rm -rf ~/.config/feedbackd
rm -rf ~/.config/assistant-button
rm -rf ~/.local/share/squeekboard


cd ~ && rm -rf .git/fastflx1

pkexec rm -rf /opt/fastflx1

