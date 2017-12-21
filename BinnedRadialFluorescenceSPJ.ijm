// The most recent update of this program was 12/21/2017
// This program was designed to measure fluorescence intensity in concentric rings 
// around the oocyte. This "bining" of fluorescence should give the user a better idea
// of regions of expression: ie: perinuclear, upper wedge, lower wedge, cortex.
//
// This program works best for oocytes closest to a circular shape. 
// User must first manually rotate the oocyte with the vegetal pole towards the bottom
// Image > Transform > Rotate > check preview, check ENGLARGE IMAGE TO FIT RESULT
//
// Input values required: center of oocyte (determine by drawing a circle around nucleus
// and using imageJ to measure "centroid". 
// Oocyte diameter, o, measured manually using the circle in imageJ
// Nucleus diameter, n, measured manually
// Maximum pixel intensity is automatically obtained, but user must define lowest % to exclude
// USE RAWINTEGRADEDDENSITY for measurements

// April 2017 update - Convert automatically to 8-bit
// December 2017 update - Additional annotation

run("8-bit"); // Can be adjusted to 16-bit
setForegroundColor(255, 255, 255);
run("Select None"); 
getStatistics(nPixels, mean, min, max); 
setThreshold(0.5*max, max);  // Adjustable Threshold.  Vary % of max until nucleus and black background is no longer included. Usually top 50% - top 80% of pixels are included.
run("Convert to Mask");
getPixelSize(unit, pixelWidth, pixelHeight);
s= 1/pixelWidth;
w= getWidth()
L= (w*sqrt(2))
x= getNumber("centroid x", 0);  // Center of oocyte, x coordinate
y= getNumber("centroid y", 0); // Center of oocyte, y coordinate
o= getNumber("oocyte diameter", 0); // Oocyte diameter
n= getNumber("nucleus diameter", 0); // Nuclear diameter

// Loop to create concentric cirlces/bins

for (p=0; p<5; p++) // Adjustable number of bins/concentric rings. Here, 5 bins are provided (p=5). 
{
	c = (o-((o-n)*(p/5))); // Change number of bins if altered in line 33
	q = (o-((o-n)*((p+1)/5))); // Change number of bins if altered in line 33
	if (c > n) {
	run("Specify...", "width=[c] height=[c] x=[x] y=[y] oval centered scaled");
		run("Make Inverse");
		run("Fill", "slice");
		
	 run("Specify...", "width=[q] height=[q] x=[x] y=[y] oval centered scaled");
		run("Fill", "slice");
		
// Loop to create rotating line
	
	for (i=0; i<=360; i++)
	{	
		makeLine (x*s, y*s, ((L*cos(i*(PI/180)))+x*s), ((L*sin(i*(PI/180)))+y*s));
		b= getProfile();
		run("Set Measurements...", "mean integrated limit redirect=None decimal=0");
		run("Measure");
	}
	IJ.renameResults("Bin" + p); // First bin will be named Bin 0
	reset();
	} 
	else {
		print("Failed at Bin " + p); // If concentric ring falls within boundary of nucleus, it (and any subsequent bins) are excluded.
	}
	
	}