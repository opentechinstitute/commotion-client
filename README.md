##Commotion Client (UNSTABLE)

The Commotion Wireless desktop/laptop client.

To allow desktop clients to create, connect to, and configure Commotion wireless mesh networks.

This repository is in active development. **IT DOES NOT WORK!** Please look at the roadmap below to see where the project is currently at.  

###FUTURE Features:

  * A graphical user interface with:
	* A "setup wizard" for quickly creating/connecting to a Commotion mesh.
    * Mesh network advances settings configuration tools
	* Commotion mesh config customizer
	* Application system with:
	  * Mesh network application viewer
	  * Client application advertisement
	* Multiple user accounts with:
	  * Seperate "Serval Keychains"
	  * Custom Network & Application Settings
  * A status bar icon for selecting, connecting to, and disconnecting from ad-hoc networks
  * A robust extension system that allows for easy customization and extension of the core platform
  * Full string translation & internationalization support
  * Built in accessability support
  
###Requirements: ( To run )

  * Python 3 or higher

###Requirements: ( To build from source )

  * Python 3.3 or higher
  * cx_freeze (See: build/README.md for instructions)
		
###Current Roadmap:

#### Version 1.0

  * Core application
    * Single application support
    * Cross-application instance messaging
    * Crash reporting 
	  * With PGP encryption to the Commotion Team
      * Crash Reporting Window
  * Main Window
  * Menu Bar
    * Automatically displays all core and user loaded extensions 
  * Task Bar
  * Extension Manager
  * Messaging manager
    * Allow extensions to talk to commotion IPC client
      * CSM and Commotiond support
  * Core Extensions
    * Commotion Config File Editor 
    * Setup Wizard (basic config walkthough)
    * Application Viewer
    * Application Advertiser
    * Welcome Page
	* Network Security Menu
	* Network Status overview 
  * Setting menu
	* Core application settings
	* Extension settings menu
	  * Settings for any extensions with custom settings pages
  * Control Panel settings menu
    * A client agnostic control panel tool for mesh-network settings in an operating systems generic control panel. 
  * Linux Support
  * Commotion Human Interface Guidelines compliant interface 
  * In-Line Documentation tranlation into developer API 
  * User Settings Manager
    * un-encrypted user settings for network configuration

#### Version 2.0

  * Setting menu
	* User settings
  * Core Extensions
    * Network vizualizer 
    * User Settings [applications]
    * User Settings [Serval & Security] 
	* REMOVE Network Security Menu as it will be replaced with user settings
  * User Settings Manager
    * GPG Encrypted user settings
	* multi-user login/logout support
  
### Version 3+.0
  * Windows Support
  * OSX Support