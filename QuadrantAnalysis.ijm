//The most recent update of this program was 04/08/2016
// The program is designed for measuring the flourescence in each 
//quadrant (veg, animal, left, right) of an oocyte
//User must first manually rotate image with oocyte vegetal pole towards the bottom
//Image > Transform > Rotate > check preview, check ENGLARGE IMAGE TO FIT RESULT
// Input values required: center of oocyte (determine by drawing a circle around nucleus
// and using imageJ to measure "centroid". 
// Defining box = box large enough to contain oocyte, user input, generally 350-450.
// Maximum pixel intensity is automatically obtained, but user must define lowest % to exclude
//USE RAWINTEGRADEDDENSITY

//defines scale (resulting from zoom and objective on scope)
getPixelSize(unit, pixelWidth, pixelHeight);
s= 1/pixelWidth

x= getNumber("enter centroid x", 254)
y= getNumber("enter centroid y", 273)
a= getNumber("bounding square size", 400)
makeRectangle((x*s)-(0.5*a*s), (y*s)-(0.5*a*s), a*s, a*s)
run("Crop");
//Defining thresholds
run("Select None");
getStatistics(nPixels,mean,min,max);
w= max
//define what lower end of pixel intensity to exclude, default = 20%. ie: Only include highest 80% of signal.  
//This step helps eliminate any background, including that outside of the oocyte frame.
m= getNumber("Exclude what % of darkest pixels? ie: 20% = 0.2", 0.20)
l= w*m

//sets threshold
setAutoThreshold("Default dark");
setThreshold(l, w);

//Draw ROI quadrants
run("Select None");
getDimensions(width,height,channels,slices,frames);
b= width
//as a square width=height

makePolygon(0, b, 0.5*b, 0.5*b, b, b) //vegetal
roiManager("Add");
makePolygon(0, 0, 0.5*b, 0.5*b, b, 0) //animal
roiManager("Add");
makePolygon(0, 0, 0.5*b, 0.5*b, 0, b) //left
roiManager("Add");
makePolygon(0.5*b, 0.5*b, b, 0, b, b) //right
roiManager("Add");
roiManager("Select", 0);
roiManager("Rename", "veg_quad");
roiManager("Select", 1);
roiManager("Rename", "an_quad");
roiManager("Select", 2);
roiManager("Rename", "left_quad");
roiManager("Select", 3);
roiManager("Rename", "right_quad");
roiManager("Select", newArray(0,1,2,3));

setOption("Show All", true);
//ROI measurements with threshold limit
run("Set Measurements...", "centroid integrated limit display redirect=None decimal=0");
roiManager("Select", newArray(0,1,2,3));

roiManager("Measure");
