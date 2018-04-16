# EX VIVO Granule Analysis Program. Updated 04/16/2018, SPJ. Written in Jython
# Using Binary FEature Extractor and Analyze Particle Plugins from Fiji/ImageJ this program determines granule count and properties based on size, shape, and overlap with DIC or background.
# The program is extremely dependent on file order.  All prompted files must be present (WT, DIC, MUT, BG). Selecting these in the appropriate space in the user dialogue will lead to duplication, renaming, and appropriate ordering of the files.  
# A future implementation of the this program may be less dependent on order, but that is not currently the case.
# 

from os import path
from java.io import File
from ij import IJ, Macro, ImagePlus, Macro, WindowManager as WM
from ij.process import ImageStatistics as IS, ImageProcessor
from ij.measure import Measurements, ResultsTable
from ij.process import ImageConverter as IC
from ij.plugin.frame import RoiManager
from ij.gui import GenericDialog, RoiProperties
from ij.io import FileSaver
from fiji.util.gui import GenericDialogPlus
import codecs
import sys
from ij.plugin import Commands, Thresholder
from ij.text import TextWindow
import re

# Sometimes JAVA/ImageJ has a problem with file names. Changing default coding should help.
reload(sys)
sys.setdefaultencoding('UTF8')

#Bring up roimanager
rm = RoiManager().getInstance()

#Set some defaults
IJ.run("Set Measurements...", "area integrated area_fraction limit display scientific redirect=None decimal=3")
IJ.setForegroundColor(0,0,0)
IJ.setBackgroundColor(255,255,255)

#User Input Dialoge
analyses = ["Counts", "ATP"]
yn = ["YES", "NO"]

gdp = GenericDialogPlus("Ex Vivo Granule Analysis")
gdp.addMessage("Choose a UNIQUE directory to save analysis files")
gdp.addDirectoryOrFileField("Output Directory", "D:/Samantha/")
gdp.addMessage("IMPORTANT: Files are tracked based on input order")
gdp.addMessage("Select input files (.tiff)...")
gdp.addFileField("Wildtype", "D:/Samantha/test/VLEwt.tif")
gdp.addFileField("DIC", "D:/Samantha/test/dic.tif")
gdp.addFileField("Mutant", "D:/Samantha/test/ddmut.tif")
gdp.addFileField("Background (DAPI)", "D:/Samantha/test/bg.tif")
gdp.addChoice("Select analysis type", analyses, "Counts")
gdp.addMessage("Choose variable conditions:")
gdp.addNumericField("Minimum Threshold. Choose value (0-1) as a percent of maximum threshold", 0.20, 2)
gdp.addNumericField("Minimum granule size (pixel^2)", 20, 0)
gdp.addNumericField("Minimum granule circularity/shape. 1.0 = perfect cirlce, 0.5 = ellipse, 0.0 = rod", 0.50, 3)
gdp.addNumericField("Maximum granule circularity", 1.00, 3)
gdp.addNumericField("Minimum percent overlap between images (0 = no overlap required, 100 = perfect overlap)", 25, 0)
gdp.addChoice("Exclude particles on outside perimeter? Recommended for ATP analysis", yn, "NO")
gdp.showDialog()
outdir = gdp.getNextString()
path_wt = gdp.getNextString()
path_dic = gdp.getNextString()
path_mut = gdp.getNextString()
path_bg = gdp.getNextString()
analysistype = gdp.getNextChoice()
uThres = gdp.getNextNumber()
uGsize = gdp.getNextNumber()
uGshape = gdp.getNextNumber()
uGshapemax = gdp.getNextNumber()
uOverlap = gdp.getNextNumber()
uExclude = gdp.getNextChoice()

# Files will automatically be output to a new Fiji_Analysis directory. If this directory already exists, files will be overwritten. This checks to make sure the directory does not yet exist.
if path.exists(outdir+File.separatorChar+"Fiji_Analysis") and path.isdir(outdir+File.separatorChar+"Fiji_Analysis"):
	gdchk = GenericDialog("WARNING")
	gdchk.addMessage("Analysis folder already exists. Choose a different directory to avoid overwritng your current data")
	gdchk.hideCancelButton()
	gdchk.showDialog()
	print "Analysis folder already exists. Choose a new directory to avoid overwriting your current analysis"
	uknow = gdchk.wasOKed()
	if uknow == True:
		IJ.getImage()

#Creates Fiji_Analysis directory.
File(outdir+File.separatorChar+"Fiji_Analysis").mkdir()
analysisOut = outdir+File.separatorChar+"Fiji_Analysis"
print analysisOut

inputPaths = [path_wt, path_dic, path_mut, path_bg]

# Since the script is critically depedent on file input order, files are duplicated and saved with easily referenced names in the new Directory.  0 = WT, 1 = DIC, 2 = MUT, 3 = BG. ALWAYS.
newPaths = []
for p in inputPaths:
	IJ.open(p)
	tmp = IJ.openImage(p)
	IJ.getImage()
	fs = FileSaver(tmp)
	if p == inputPaths[0]:
			dup_wt = "wt1.tif"
			newPaths.append(analysisOut+File.separatorChar+dup_wt)
			fs.saveAsTiff(analysisOut+File.separatorChar+dup_wt)
	if p == inputPaths[1]:
			dup_dic = "dic1.tif"
			newPaths.append(analysisOut+File.separatorChar+dup_dic)
			fs.saveAsTiff(analysisOut+File.separatorChar+dup_dic)
	if p == inputPaths[2]:
			dup_mut = "mut1.tif"
			newPaths.append(analysisOut+File.separatorChar+dup_mut)
			fs.saveAsTiff(analysisOut+File.separatorChar+dup_mut)
	if p == inputPaths[3]:
			dup_bg = "bg1.tif"
			newPaths.append(analysisOut+File.separatorChar+dup_bg)
			fs.saveAsTiff(analysisOut+File.separatorChar+dup_bg)

	print "new paths assigned"

print len(newPaths), "New Paths= ", newPaths
Commands.closeAll()

# Closes original images and just opens duplicates with specific file names in new directory
for image in newPaths:
	IJ.open(image)
	IJ.run("8-bit")
	thisImage = IJ.openImage(image)
	# Because of the shadowy-grey background of the DIC image, setting the lower threshold to 20% of it's maximum does not work. Setting the lower threshold to 20% of the wildtype image's max threshold works well, and is a good compromise.
	if image == newPaths[0]:
		wtImageThreshold = thisImage.getStatistics(Measurements.MIN_MAX).max
	if image == newPaths[1]:
		maxThreshold = wtImageThreshold
	else:
		maxThreshold = thisImage.getStatistics(Measurements.MIN_MAX).max
	IJ.setThreshold(uThres*maxThreshold, maxThreshold)
	#print image, ImagePlus.getTitle(thisImage) 
## good troubleshooting check; don't delete comment
	print "max threshold=", maxThreshold
	IJ.run("Convert to Mask")
	if analysistype == "Counts":
		if uExclude == "NO":
			IJ.run("Analyze Particles...", "size="+str(uGsize)+"-Infinity pixel circularity="+str(uGshape)+"-"+str(uGshapemax)+" show=[Overlay Masks] clear summarize add")
			print "Counts, Include all"
		else:
			IJ.run("Analyze Particles...", "size="+str(uGsize)+"-Infinity pixel circularity="+str(uGshape)+"-"+str(uGshapemax)+" show=[Overlay Masks] exclude clear summarize add")
			print "Counts, Exclude edges"
	if analysistype == "ATP":
		IJ.run("Fill Holes")
		if uExclude == "YES":
			IJ.run("Analyze Particles...", "size="+str(uGsize)+"-Infinity pixel circularity="+str(uGshape)+"-"+str(uGshapemax)+" show=[Overlay Masks] exclude clear summarize add")
			print "ATP, Exclude edges"
		else:
			IJ.run("Analyze Particles...", "size="+str(uGsize)+"-Infinity pixel circularity="+str(uGshape)+"-"+str(uGshapemax)+" show=[Overlay Masks] clear summarize add")
			print "ATP, include all"
	# ROI management
	rm.runCommand("Combine")
	rm.runCommand("Add")
	rct = rm.getCount()
	fullTitle = ImagePlus.getTitle(thisImage)
	shortTitle = ImagePlus.getShortTitle(thisImage)
	IJ.run("Invert LUT")   ### Invert LUT
	rm.rename(rct-1, str(shortTitle))
	rm.select(rct-1)
	if image == newPaths[0]:
		rm.runCommand("Save", analysisOut+File.separatorChar+"ROIindividual_wt"+".zip")
	if image == newPaths[1]:
		rm.runCommand("Save", analysisOut+File.separatorChar+"ROIindividual_dic"+".zip")
	if image == newPaths[2]:
		rm.runCommand("Save", analysisOut+File.separatorChar+"ROIindividual_mut"+".zip")
	if image == newPaths[3]:
		rm.runCommand("Save", analysisOut+File.separatorChar+"ROIindividual_bg"+".zip")
	rm.setSelectedIndexes(range(0, rct-1))
	x = rm.getSelectedIndexes()
	rm.runCommand("Deselect")
	rm.setSelectedIndexes(x)
	rm.runCommand("Delete")
	rm.select(0)
	if image == newPaths[0]:
		rm.runCommand("Save", analysisOut+File.separatorChar+"ROIcombo_wt"+".zip")
	if image == newPaths[1]:
		rm.runCommand("Save", analysisOut+File.separatorChar+"ROIcombo_dic"+".zip")
	if image == newPaths[2]:
		rm.runCommand("Save", analysisOut+File.separatorChar+"ROIcombo_mut"+".zip")
	if image == newPaths[3]:
		rm.runCommand("Save", analysisOut+File.separatorChar+"ROIcombo_bg"+".zip")
	rm.select(0)
	IJ.run("Clear Outside")
	IJ.run("Hide Overlay")
	# Mostly here to avoid an annoying popup about closing unsaved windows. Just saves some intermediately processsed images.
	aptitles = WM.getImageTitles()
	for tmpap in aptitles:
		if re.search("1.tif", tmpap):
			IJ.selectWindow(tmpap)
			apimp = IJ.getImage()
			fsap = FileSaver(apimp)
			fsap.saveAsTiff(analysisOut+File.separatorChar+"tmp_"+tmpap)
	print "Analyze Particles Done" #don't delete this print

# Save first analyze particles data table. This contains all elements that look like a granule based on dialogue-box speicfied conditions. It does not account for overlap wtih other images (DIC/mutant/bg)
IJ.selectWindow("Summary")
IJ.saveAs("Text", analysisOut + File.separatorChar + "Summary_Particles.txt")
summarywindow = "Summary_Particles.txt"
IJ.selectWindow(summarywindow)
IJ.run("Close")
rm.reset()
file_paths = []
for folder, subs, files in os.walk(analysisOut):
  for filename in files:
    file_paths.append(os.path.abspath(os.path.join(folder, filename)))
    print "file paths done"

#More ROI management
roicombo = []
for fp in file_paths:
	if "ROIcombo_" in fp:
		roicombo.append(fp)
	print "roi append done"

rm.reset()
for roifile in roicombo:
	rm.runCommand("Open", roifile)
	print "roicombo"

# Processed images are binary, 8 bit.  THIS IS A GOOD PLACE TROUBLESHOOT AND CHECK FOR ERRORS.  "Processed_*.tif" files should have a WHITE background with BLACK granules. If this is inverted, add in a an Invert LUT command:  IJ.run("Invert LUT"). Or try commenting out Invert statement on line 150.
processed_images = []	
for image in newPaths:
	IJ.open(image)
	IJ.run("8-bit")
	thisImage = IJ.openImage(image)
	title = ImagePlus.getTitle(thisImage)
	IJ.selectWindow(title)
	imp = IJ.getImage()
	fs = FileSaver(imp)
	if image == newPaths[0]:
		filepath = analysisOut+File.separatorChar+"processed_"+"wt1"+".tif"
	if image == newPaths[1]:
		filepath = analysisOut+File.separatorChar+"processed_"+"dic1"+".tif"
	if image == newPaths[2]:
		filepath = analysisOut+File.separatorChar+"processed_"+"mut1"+".tif"
	if image == newPaths[3]:
		filepath = analysisOut+File.separatorChar+"processed_"+"bg1"+".tif"
	fs.saveAsTiff(filepath)
	processed_images.append(filepath)
	print "lut done"

# another step to avoid bothersome popups. also saves some intermediate steps.	
luttitles = WM.getImageTitles()
for luts in luttitles:
	if re.search("1.tif", luts):
		IJ.selectWindow(luts)
		lutimp = IJ.getImage()
		fsap = FileSaver(lutimp)
		fsap.saveAsTiff(analysisOut+File.separatorChar+"tmp_"+luts)
	print "saved tmp images"
Commands.closeAll()

# Close all open images, and now just open the newly saved "processed_" files. AGAIN: These need a WHITE background with BLACK granules.
file_paths2 = []
for folder, subs, files in os.walk(analysisOut):
  for filename in files:
    file_paths2.append(os.path.abspath(os.path.join(folder, filename)))
    print "file paths done"

proc = []
for fp in file_paths2:
	if "processed_" in fp:
		proc.append(fp)
	print "proc.done"

for procImages in proc:
	IJ.open(procImages)
	tmp = IJ.openImage(procImages)
	title = ImagePlus.getTitle(tmp)
	IJ.selectWindow(title)
	#Another Invert LUT --- for the Binary Feature Extractor below images need to have a black background and white granules.  
	IJ.run("Invert LUT")
	print "new proc opened"
	

	#wfd = WAIT("Pause then BFE")
	#wfd.show()

# Binary Feature Extractor from the BioVoxxel plugin.  This will compare two images for overlaping particles.  Takes into account a minimum overlap, but does not yet consider size and shape. 
objectsB = ["processed_wt1.tif", "processed_dic1.tif", "processed_mut1.tif", "processed_bg1.tif"]

for index, obj in enumerate(objectsB):
	for s, sels in enumerate(objectsB):
		if s != index:
			IJ.run("Binary Feature Extractor", "objects="+obj+" selector="+sels+" object_overlap="+str(uOverlap)+" combine count")
	print "BFE done"

titles=[]
titles = WM.getImageTitles()
#Saves BFE extracted images, as Extracted_processsed_*.  These are really just temporary files, but a good TROUBLSHOOTING check. The saved files should ahve a black background with white granules.
for extracted in titles:
	if re.search("Extracted", extracted):
		IJ.selectWindow(extracted)
		bfe=IJ.getImage()
		fsb = FileSaver(bfe)
		fsb.saveAsTiff(analysisOut+File.separatorChar+extracted)
		IJ.selectWindow(extracted)
	# Analyze Particles now examines the the overlapping particles for user specified granule properties -- size and shape.
		#IJ.run("Invert LUT")
		IJ.run("Analyze Particles...", "size="+str(uGsize)+"-Infinity pixel circularity="+str(uGshape)+"-"+str(uGshapemax)+" show=[Overlay Masks] summarize add")
		print "Analyze Particles on overlapping elements done"
		
rm.runCommand("Save", analysisOut+File.separatorChar+"allfinalROIs"+".zip")
#rm.runCommand("Close")
		
moretitles = []
moretitles = WM.getImageTitles()
for more in moretitles:
	if re.search("1.tif", more):
		IJ.selectWindow(more)
		moreimp = IJ.getImage()
		fsm = FileSaver(moreimp)
		fsm.saveAsTiff(analysisOut+File.separatorChar+"tmp2_"+more)
	print "saved tmp2 images"


#Rename elements in data tables, so they make sense......
rt = WM.getWindow("BFE_Results").getTextPanel().getOrCreateResultsTable()
abbrv = ["WT", "DIC", "MUT", "BG"]
row = -1

for a in abbrv:
	for b in abbrv:
		if a != b:
			row = row+1
			rt.setValue(0,row, "BFE:  "+a+"_(obj)"+" vs. "+b+"_(sel)")
			rt.show("BFE_Results")
			print "renamed elements BFE table"
			
IJ.selectWindow("BFE_Results")
IJ.saveAs("Text", analysisOut+File.separatorChar+"BFE_results.txt")

rtAP = WM.getWindow("Summary").getTextPanel().getOrCreateResultsTable()
AProw = -1
for ap in abbrv:
	for bp in abbrv:
		if ap != bp:
			AProw = AProw+1
			rtAP.setValue(0,AProw, "AP:  "+ap+"_(obj)"+" vs. "+bp+"_(sel)")
			rtAP.show("Summary")
	print "renamedelements AP table"
	
IJ.selectWindow("Summary")
IJ.saveAs("Text",analysisOut+File.separatorChar+"AP.Granule_Results.txt")
print "Saving GRANULE data table finished"
Commands.closeAll()
#rm.reset()

IJ.beep() #specifically for chris
gdp = GenericDialogPlus("Ex Vivo Granule Analysis")
gdp.addMessage("DING!!! DING!!! Analysis Complete!")
gdp.showDialog()
IJ.beep()



