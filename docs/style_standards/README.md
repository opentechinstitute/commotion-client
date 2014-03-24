# Code Standards

## Style

The code base should comply with [PEP 8](http://legacy.python.org/dev/peps/pep-0008/) styling. 

## Documentation and Doc-Strings

Doc Strings should follow the Google style docstrings shown in the google_docstring_example.py file contained in this folder.

## Logging

### Code

#### Proper Logging

Every functional file should import the "logging" standard library and create a logger that is a decendant of the main commotion_client logger.

```
import logging

...

self.log = logging.getLogger("commotion_client."+__name__)
```

#### Logging and translation

We use the PyQt translate library to translate text in the Commotion client. The string ``logs``` is used as the "context" for all logging objects. While the translate library will automatically add the class name as the context for most translated strings we would like to seperate out logging strings so that translators working with the project can prioritize it less than critical user facing text.

```
_error = QtCore.QCoreApplication.translate("logs", "That is not a valid extension config value.")
self.log.error(_error)
```

Due to the long length of the translation call ``QtCore.QCoreApplication.translate``` feel free to set this value to the variable self.translate at the start of any classes. Please refrain from using another variable name to maintain consistancy actoss the code base.

```self.translate = QtCore.QCoreApplication.translate```

### LogLevels

Logging should correspond to the following levels:

  * critical: The application is going to need to close. There is no possible recovery or alternative behavior. This will generate an error-report (if possible) and is ABSOLUTELY a bug that will need to be addressed if a user reports seeing one of these logs.
  
  * error & exception: The application is in distress and has visibly failed to do what was requested of it by the user. These do not have to close the application, and may have failsafes or handling, but should be severe enough to be reported to the user. If a user experiences one of these the application has failed in a way that is a programmers fault. These can generate an error-report at the programmers discression.

  * warn: An unexpected event has occured. A user may be affected, but adaquate fallbacks and handling can still provide the user with a smooth experience. These are the issues that need to be tracked, but are not neccesarily a bug, but simply the application handling inconsistant environmental conditions or usage.

  * info: Things you want to see at high volume in case you need to forensically analyze an issue. System lifecycle events (system start, stop) go here. "Session" lifecycle events (login, logout, etc.) go here. Significant boundary events should be considered as well (e.g. database calls, remote API calls). Typical business exceptions can go here (e.g. login failed due to bad credentials). Any other event you think you'll need to see in production at high volume goes here.

  * debug: Just about everything that doesn't make the "info" cut... any message that is helpful in tracking the flow through the system and isolating issues, especially during the development and QA phases. We use "debug" level logs for entry/exit of most non-trivial methods and marking interesting events and decision points inside methods.

### Logging Exeptions

Exceptions should be logged using the exception handle at the point where they interfeir with the core task. If you wish to add logging at the point where you raise an exception use a debug or info log level to provide information about context around an exception.

## Exception Handling


## Code

### Python Version
All code MUST be compatable with Python3.
