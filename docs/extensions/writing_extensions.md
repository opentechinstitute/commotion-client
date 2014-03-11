# Writing Extensions

## Intro

This documentation will walk you through how to create a Commotion Client extension using the provided templates and Qt Designer. This documentation follows the development of the core extension responsable for managing Commotion configuration files. You can find the code for the version of the extension built in this tutorial in the "docs/extensions/tutorial" folder. The current Commotion config extension can be found in "commotion_client/extension/core/config_manager." This tutorial will not keep up to date with this extension as it evolves unless there are core changes in the commotion API that require us to update sections to maintain current with the API.

## Design

Commotion comes with a [JSON](http://json.org/) based network configuration file. This file contains the mesh settings for a Commotion network. These profiles currently contain the following values.
```
{
  "announce": "true",
  "bssid": "02:CA:FF:EE:BA:BE",
  "bssidgen": "true",
  "channel": "5",
  "dns": "208.67.222.222",
  "domain": "mesh.local",
  "encryption": "psk2",
  "ip": "100.64.0.0",
  "ipgen": "true",
  "ipgenmask": "255.192.0.0",
  "key": "c0MM0t10n!r0cks",
  "mdp_keyring": "/etc/commotion/keys.d/mdp.keyring/serval.keyring",
  "mdp_sid": "0000000000000000000000000000000000000000000000000000000000000000",
  "mode": "adhoc",
  "netmask": "255.192.0.0",
  "serval": "false",
  "ssid": "commotionwireless.net",
  "type": "mesh"
}
```

Any good user interface starts with a need and a user needs assessment. We *need* an interface that will allow a user to understand, and edit a configuration file. Our initial *user needs assessment* revealed two groups of users.

Basic Users:
  * These users want to be able to download, or be given, a config file and use it to connect to a network with the least ammount of manipulation.
  * These users want interfaces based upon tasks, not configuration files, when they do modify their settings.
  * When these users download a configuration file they want it to be named somthing that allows it to be easy to identify later/

Intermediate/Advanced Users
  * These users desire all the attributes that are listed under the *basic user.*
  * These users also want an interface where they can quickly manipulate all the network settings quickly without having to worry about abstractions that have been layered on for new users.
    * These abstractions make advanced users feel lost and frustrated because they know what they want to do, but can not find the "user friendly" term that pairs with the actual device behavior. 


Our needs assessment identified two different extensions. One extension is a device configuration interface that abstracts individual networking tasks into their component parts for easy configuration by a new user. The second extension is a configuration file loader, downloader,  editor, and applier. This second extension is what we will build here.

The Commotion [Human Interface Guidelines](http://commotionwireless.net/developer/hig/key-concepts) have some key concepts for user interface that we should use to guide our page design.

**Common Language:** The Commotion config file uses a series of abbreviations for each section. Because this menu is focused on more advanced users we should provide not only the abbreviation, but the technical term for the object that any value interacts with.

**Common UI Terms:** Beyond simply the config file key, and the true technical term, as new users start to interact more competantly with Commotion it will be confusing if the common terms we use in the basic interfaces is not also included. As such we will want to use the *common term* where one exists. 

Taking just one value we can sketch out how the interface will represent it.

```"ssid": "commotionwireless.net"```

![A sketch of a possible SSID including all terms.](tutorial/images/design/ssid_sketch.png)

Beyond the consitancy provided by common terms, common groupings are also important. In order to ensure that a user can easily modify related configurations. We have grouped the configuration values in the following three groups.

security {
  "announce"
  "encryption"
  "key
  "mdp_keyring"
  "mdp_sid"
  "serval"
}

network {
  "channel"
  "mode"
  "type"
  "ssid"
  "bssid"
  "bssidgen"
  "domain"
  "netmask"
}

local {
  "ip"
  "ipgen"
  "ipgenmask"
  "dns"
}


TODO:
  * Show process of designing section headers
  * Show final design

## The Qt Designer

Now that we have the basic layout we can go to Qt Designer and create our page. Qt Designer is far more full featured than what we will cover here. A quick online search will show you far better demonstrations than I can give. Also, showing off Qt is not the focus of this tutorial.

First we create a new dialogue. Since our design was a series of sections that are filled with a variety of values I am going to start by creating a single section title.


Using our design document I know that I want the section header to be about 15px and bold. I can do this in a few ways. I can set the font directly in the "property editor", use the "property editor" to create a styleSheet to apply to the section header, or use an existing style sheet using the "Add Resource" button in the styleSheet importer or in the code. I recoomend the last option because you can use existing Commotion style sheets to make your extension fit the overall style of the application. The "Main" section will have instructions on how to apply a existing Commotion style sheet to your GUI.

<pictures of the three ways to style a item.>

Feel free to use whatever works for you. To make it easy for me to create consistant styling later I am just going to do everything unstyled in the Qt Designer and then call in a style-sheet in the "Main" section.

Not that I have my section header I am going copy it three times and set the "objectName" and the user-facing text of each. Once this extension is functional I will go back through and replace all the text with user-tested text. For now, lets just get it working.

<picture of settings text in place.>

Now that are section headers are created we are goign to have to go in and create our values. Qt Designer has a variety of widgets that you can choose from. I am only going to go over two types of widgets to show you how to put them together.

First we are going to make a simple text-entry field following the design we created before. The following was created using four "label's" and one "plain text edit" box.

<picture of plain dialogue settings.> 

I used a label for the question mark icon because non-interactive icons are easily made into graphics by using the "property editor." In the QLabel section click the "pixmap" property and choose "Choose Resource" in the dropdown menu to the right. This will allow you to choose a resource to use for your image. You can choose the "commotion_client/assets/commotion_assets.qrc" file to use any of the standard Commotion icons. We have tried to make sure that we have any sizes you might need of our standard icons.



## Stylesheets

## Unit Tests

## The Config

## The Backend

### Main

### Settings

### Taskbar

