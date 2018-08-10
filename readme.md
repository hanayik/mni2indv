# Introduction

In some cases it's beneficial to define landmarks within a template (a single operation). Then, we might want to define those landmarks in many different individual subjects. Rather than starting from scratch, this code makes the process much faster, but requires fine tuning the landmarks once they are created in subject space.

## Requirements

- FSL must be installed
- Uses bet, flirt, img2imgcoord
- Must supply .anat file (produced from MRIcron) and the image the .anat file landmarks were defined in
- Must also supply a subject's T1w image to translate the landmarks to

## TODO

- clean up code
- make stable for edge cases