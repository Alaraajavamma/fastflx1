# FastFLX1 - some tweaks for best linux phone in the market

This simple tool adds some small tweaks to your FLX1. 
**Notice: If you have done some own tweaks to your ~. files it might be good idea to make backup because this setup will override some of them.**

Update or remove this via desktop actions - aka. long press from the desktop icon

Mainly: 
1. Alarm volume script which will ensure that your alarm clock will allways play with full sound - and GUI interface to restart this service script if it fails
2. Dialtone script which will make your phone vibrate and blink led in interval when you are calling out (most carriers does not generate dialtone sound in VoLTE so this kind of replaces it) - and GUI interface to restart this service script if it fails
3. Simple GUI interface for changing from staging to prod or via versa - or upgrade your system trough terminal 
4. GUI interface for changing Squeekboard layout 
5. Asisstant-button tweaks which are partially work-in-proggress but it shows proof-of-concept how to make assintant-button behave differentially based on certain conditions (locked / unlocked currently) 
6. Disable annoying volume change sound (blop - blop when change volume) - for this you need also change once some default notification sound from phosh-mobile-settings - feedback (no idea why but it somehow activates the __custom sound theme which is kind of needed to make this work)
7. If you use finnish layout in squeekboard you will get the ultimate universal layout made by me 

I am working on this slowly and will add more (GUI) features soonish (or remove some parts what Barry and Jesus from Furilabs make unnecessary ;) ). If you wan't to help feel free to send me message, open issue or so. 

![FastFLX1 in action](fastflxsc.png)

## How to install?

`sudo apt install git && cd ~ && mkdir -p .git && cd .git && git clone https://gitlab.com/Alaraajavamma/fastflx1 && cd fastflx1 && sudo chmod +x install.sh && ./install.sh `

And it should just work

Remove?

`cd ~ && cd .git && cd fastflx1 && ./uninstall.sh`


## License
Feel free to do what ever you want with this but no guarantees - this will probably explode your phone xD

## Something else?
If you wan't to help or find issue feel free to contact

