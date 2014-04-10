##Commotion Client (UNSTABLE)

The Commotion Wireless desktop/laptop client.

To allow desktop clients to create, connect to, and configure Commotion wireless mesh networks.

This repository is in active development. IT DOES NOT WORK! Please look at the roadmap below to see where the project is currently at.  

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

  * Core application
    * Single application support
    * Cross-application instance messaging
    * Crash reporting 
	  * With PGP encryption to the Commotion Team (planned)
	* unit tests (planned)
  * Main Window
    * unit tests (planned)
  * Menu Bar
    * Automatically displays all core and user loaded extensions (planned)
	* Unit Tests (planned)
  * Task Bar
    * unit tests (planned)
  * Extension Manager
    * unit tests (planned)
  * Core Extensions
    * Network vizualizer (planned)
	  * unit tests (planned)
    * Commotion Config File Editor (planned)
	  * unit tests (planned)
    * Setup Wizard (planned)
	  * unit tests (planned)
    * User Settings [applications] (planned)
	  * unit tests (planned)
    * User Settings [Serval & Security] (planned)
	  * unit tests (planned)
    * Application Viewer (planned)
	  * unit tests (planned)
    * Application Advertiser (planned)
	  * unit tests (planned)
    * Welcome Page (planned)
	* Crash Window
	  * unit tests  (planned)
	* Network Status overview (planned)
 	  * unit tests (planned)
  * Setting menu
    * unit tests (planned)
	* Core application settings
	  * unit tests (planned)
	* User settings
	  * unit tests (planned)
	* Extension settings menu
	  * unit tests (planned)
	  * Settings for any extensions with custom settings pages
  * Commotion Service Manager integration
    * unit tests (planned)
	* CSM python bindings
	* Threaded messaging to CSM (planned)
	* Application viewer (planned)
	* Application advertiser (planned)
  * Commotion Controller
    * unit tests (planned)
	* Threaded messaging (planned)
	* Messaging objects to pass to extensions (planned)
	* Network agent interceptor [for extending commotiond functionality across platforms] (planned)
	* Commotiond integration (planned)
  * Control Panel settings menu
    * A client agnostic control panel tool for mesh-network settings in an operating systems generic control panel. (planned)
	* unit tests (planned)
  * Linux Support (planned)
  * Windows Support (planned LONGTERM)
  * OSX Support (planned LONGTERM)
  * Commotion Human Interface Guidelines compliant interface (planned)
  * In-Line Documentation tranlation into developer API (planned)
  
  
	
