## Summary
Kivy lang syntax highligh and autocompletion.


## How to Use
####for widget/class scope auto-completetion.

[alt tag](scope1.png) [alt tag](scope2.png)
enter code under widget or hit enter on empty line to trigger code hint


####for kivylang import auto-completetion.
[alt tag](import1.png) [alt tag](import2.png) [alt tag](import3.png) [alt tag](import4.png) 


### Configure setting
Theoretically, no configuration is needed.( I'm not quite familiar with sublime configuration, so just raise an issue if you have problem running this plugin)
In case your hightlight did not work!

```json
{
    "auto_complete_triggers":
    [
        {
            "characters": "qazwsxedcrfvtgbyhnujmikolpQAZWSXEDCRFVTGBYHNUJMIKOLP.\n ",
            "selector": "source.python.kivy"
        }
    ],
    "color_scheme": "Packages/KivyLang/KivyLang.tmTheme",
    "font_size": 9,
    "theme": "KivyLang.sublime-theme",
    "kivy_path": "",            //not implement yet
    "template_runner": "",      //not implement yet
    "ps_path": ""               //not implement yet
}

```

### make Auto-completion for user defined lib
For the reason that this plugin achievved auto-compoletion by searching api2.txt which fetched from kivy pdf manual. Due to it's fetched from kivy pdf manual, dirty and not well categorized, not only kivylang exposed api but also kivy were show up. If you want to add user defined lib and make it to recognize which content to show up, you have to add your user defined lib under api2.txt and comply with the existing rule. Which is:

{property_or_methods}{space}{(your.library.path)}{newline}
- for example:

anchor_x (kivy.uix.anchorlayout.AnchorLayout)
anchor_y (kivy.graphics.svg.Svg attribute)

if you have a better api please let me know!




### Install
* for windows:
    copy all the files into C:\Users\{user_name}\AppData\Roaming\Sublime Text 3\Packages\KivyLang

* for linux:

* for mac:
