# INF8770 Lab2 - Block-matching-algorithm

In this project you will find an exhaustive brut force search algorithm of block-matching in order to compress video 
sequence.

## Run the algorithm on a video sequence

To run the block matching algorithm in the terminal : 
```
python main.py VIDEO_SEQUENCE_PATH
```
* VIDEO_SEQUENCE_PATH is a string to the directory of the video sequence of 15frames <br>
Be sure to have python and all packages installed.

## Run the video sequence extractor

To extract frames from video run :
```
python gettrame.py VIDEO_PATH START_INDEX SAVE_DIRECTORY_PATH
```
* VIDEO_PATH the path to the video 
* START_INDEX the index of the first frame
* SAVE_DIRECTORY_PATH the path to the directory to save the list of 15 frames

## Source 

* Code : 
  - https://github.com/javiribera/frame-block-matching
  - https://moodle.polymtl.ca/course/view.php?id=1396
  - https://www.delftstack.com/fr/howto/matplotlib/how-to-plot-a-2d-heatmap-with-matplotlib/
  - https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames
* Video :
  - https://www.youtube.com/watch?v=2UEkizpGKDU / Sequence fix : from frame 1600 at 1min06 / Sequence mvt : from frame 
  2910 at 2min01
