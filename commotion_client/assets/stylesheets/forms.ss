/*

Commotion style sheet for entry forms.

Color Pallet:

PRIMARY COLORS
  * White FFFFFF
  * Black 000000
  * Pink FF739C
  
SECONDARY COLORS
  * Electric Yellow E8FF00
  * Electric Purple 877AED
  * Electric Green  00FFcF
  * Blue 63CCF5 
  * Gold C7BA38
  * Grey E6E6E6

Color Usage Ratio:
  * 70% White
  * 15% Black
  * 10% Pink
  * 5% Electric Purple

Font Sizeing:
  * 40 px Headings
  * 13 Px [ALL CAPS]: Subheadings
  * 13 px: Body Text
per: https://github.com/opentechinstitute/commotion-docs/blob/staging/commotionwireless.net/files/HIG_57_0.png *They meant pixel, not point.

  */

/* Defaults */
* { font-size: 13px; }

/* Section Header */
.QLabel[style_sheet_type = "section_header"] {
	font-size: 40px;
	font-style: bold;
}

/* Value Header */
.QLabel[style_sheet_type = "value_header"] {
	color: #877AED;
	font-style: bold;
}

/* Help Pop Up */
.QToolTip[style_sheet_type = "value_help_text"] { background-color: #E6E6E6 }

/* Help Text */
.QLabel[style_sheet_type = "help_text"] { font-style: italic; }

/* Static / Automatic / Unchangable Value */
.QLabel[style_sheet_type = "help_text"] { background-color: #E6E6E6 }
