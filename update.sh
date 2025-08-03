#!/bin/bash

"${HOME}/.git/fastflx1/uninstall.sh"

echo "Uninstall script finished."

sudo apt install git && cd ~ && mkdir -p .git && cd .git && git clone https://gitlab.com/Alaraajavamma/fastflx1 && cd fastflx1 && sudo chmod +x install.sh && ./install.sh 
