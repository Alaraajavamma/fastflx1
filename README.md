# FastFLX1 - some tweaks for best linux phone in the market

This simple tool adds some small tweaks to your FLX1. 
**Notice: If you have done some own tweaks to your ~. files it might be good idea to make backup because this setup will override some of them. This includes also changes what are done via GUI but actually happens in ~. files like changing ringtone from Phosh-mobile-settings**

Update or remove this via desktop actions - aka. long press from the desktop icon

Mainly: 
1. Alarm volume script which will ensure that your alarm clock will allways play with full sound - and GUI interface to restart this service script if it fails
2. Dialtone script which will make your phone vibrate and blink led in interval when you are calling out (most carriers does not generate dialtone sound in VoLTE so this kind of replaces it) - and GUI interface to restart this service script if it fails
3. Simple GUI interface for changing from staging to prod or via versa - or upgrade your system trough terminal - or install/uninstall experimental Branchy app
4. GUI interface for changing Squeekboard (the virtual keyboard) scaling 
5. Asisstant-button tweaks which are partially work-in-proggress but it shows proof-of-concept how to make assintant-button behave differentially based on certain conditions (locked / unlocked currently) 
6. Disable annoying volume change sound (blop - blop when change volume) - and add better alarm tone. This works now ootb.
7. If you use finnish layout in squeekboard you will get the ultimate universal layout made by me
8. Provide thumbnails (image preview) for all images which are located in home folder but not in hidden folders. Now you can see what file you are choosing when you use file picker - or when you browse your files trough Nautilus. This is build as service which will also monitor new images, name changes, moved images etc. And GUI interface to restart this service script if it fails
9. Added some cool swipe gestures using lisgd - options are endless but for now they will change active apps, kill active app or press ctrl+a (look intro below)
10. Added some shortcuts when you press volume-buttons - options are endless but for now they will use wl-paste to paste the clipboard content (works in terminal), take screenshot, scale display

**Default assistant-button options:**

- Unlocked short-press = opens clipboard shortcuts (copy, paste, cut, terminal paste, and ctrl+a + copy)
- Unlocked double-press = opens display scaling shortcuts (300%, 250%, 200%, 150% or 100%)
- Unlocked long-press = back button
- Locked / on lock screen short-press = toggle the feedback theme (full - silent - quiet)
- Locked / on lock screen double-press = toggle flashlight
- Locked / on lock screen long-press = it will forcefully close all resource intensive apps

**Default volume-buttons options:**

- They will change volume so that does not change
- Short presses - first VolUp and right after VolDown = it will take picture with backcamera
- Short presses - first VolDown and right after VolUp = it will take screenshot and save it to Pictures folder
- Short presses - first two times VolUp and right after two times VolDown = opens selection where you can stop, start or restart android container
- Short presses - first two times VolDown and right after two times VolUp = opens selection where you can pkill -f most ram hungry apps (excluding android container apps and some core apps)

**Default swipe gestures:**
Notice that swipe gestures works ootb like this when FLX1 is in default portrait mode
- From the bottom swipe from left to right and it will change the open app which is on the right side of your current active window
- From the bottom swipe from right to left and it will change the open app which is on the left side of your current active window
- From the top swipe with two fingers directly down and it will "press" ctrl+a
- From top swipe with three fingers directly down and it will kill currently active app

I am working on this slowly and will add more (GUI) features soonish (or remove some parts what Barry and Jesus from Furilabs make unnecessary ;) ). If you wan't to help feel free to send me message, open issue or so. 

![Swipe gestures](gestures.png)

![FastFLX1 in action](fastflxsc.png)

## How to install?

`sudo apt install git && cd ~ && mkdir -p .git && cd .git && git clone https://gitlab.com/Alaraajavamma/fastflx1 && cd fastflx1 && sudo chmod +x install.sh && ./install.sh `

And it should just work

Remove?
Long press desktop icon and it will give you option to Uninstall. Or you can: 
`cd ~ && cd .git && cd fastflx1 && ./uninstall.sh`


## License
Feel free to do what ever you want with this but no guarantees - this will probably explode your phone xD

## Something else?
If you wan't to help or find issue feel free to contact

