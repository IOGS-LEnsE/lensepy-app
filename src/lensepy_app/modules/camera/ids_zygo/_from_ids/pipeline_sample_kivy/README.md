# Graphical kivy pipeline sample

This sample demonstrates how to use the `ids_peak_icv` default pipeline
together with the `ids_peak_afl` auto-feature module.

All device-specific behavior, such as setting exposure, framerate, and
supported pixel formats, is encapsulated in `camera.py`.

The `DefaultPipelineSample` class in `main.py` focuses on building the user interface
and interacting directly with the default pipeline.
`DefaultPipeline` provides convenient properties for adjusting pipeline
settings such as output pixel format, host gain, binning, and more.

Custom widgets used by this sample are defined in `custom_widgets.py`.

## Requirements
This sample depends on the following third-party packages:
* `kivy >= 2.3`
* `kivymd2 >=2.0` (or `kivymd >= 2.0` once released)
* `plyer`

It is also designed to work with these `IDS Peak` packages:
* `ids_peak_common >= 1.1.0`
* `ids_peak_ipl >= 1.17.1`
* `ids_peak_icv >= 1.0.0`
* `ids_peak >= 1.13.0`
* `ids_peak_afl >= 2.0.0`

To install all required dependencies, use the provided `requirements.txt`:
```
pip install -r requirements.txt
```

In addition, a suitable GenTL must be installed, for example via the `IDS Peak` setup.

## Running the sample

After installing all requirements the sample can be run by executing `main.py` with the Python interpreter

```
python main.py
```

or, if Python files (*.py) are associated with the Python interpreter, by double-clicking the file.

## Notes

### General notes

* Kivy and OpenGL use a coordinate system that is inverted relative to
  the camera image.
  To account for this, the sample enables vertical image flipping using
  the ReverseY node.
* The flip state is normally restored when the application exits.
  However, if the program terminates unexpectedly, the state may not
  reset correctly.

  If this occurs, reload the default user settings in the camera software
  to restore normal behavior.
* Due to this coordinate inversion, clockwise rotations performed in
  this sample will appear as counter-clockwise rotations when the same
  pipeline settings are loaded in other applications.

### Notes on linux

The plyer file chooser used in this sample requires one of the following command line tools to be installed:
* zenity (GTK)
* yad (a zenity fork)
* kdialog (KDE)

If none of these utilities are available, a dialog will notify the user, 
and loading or saving pipeline settings will not be possible.

Note for Python 3.12 or later: If you’re using plyer 2.1.0 or earlier, you must install `setuptools`.
