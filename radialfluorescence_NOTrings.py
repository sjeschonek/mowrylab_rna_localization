// The most recent update of this program was 04/08/2016
// This program was designed to measure fluorescence as it is distributed across the oocyte
// The program draws a line from the center of the oocyte and has it travel 360 degrees around the oocyte
// The flourescence intensity is averaged across each line, yielding 360 data points.
// The RawIntDen can be plotted against each data point (1-361)
// The result is a graph showing the radial distribution of fluorescence

// This program works best for oocytes closest to a circular shape. 

// User must first manually rotate the oocyte to the desired position.  
// I generally orient the vegetal pole to the left (9 o'clock position), as it will center the fluorescence peak
// at the vegetal wedge in the graph
// Image > Transform > Rotate > check preview, check ENGLARGE IMAGE TO FIT RESULT
//
// Input values required: center of oocyte (determine by drawing a circle around nucleus
// and using imageJ to measure "centroid". 


setForegroundColor(255, 255, 255);
run("Select None"); 
//Can adjust minimum threshold of intensity. Here, the lower 10% of pixels is excluded. This reduces background.
getStatistics(nPixels, mean, min, max); 
setThreshold(0.1*max, max)
run("Convert to Mask");
// s = scale, and is based on the zoom and objective the image was taken at. 
// You can manually find this value located at Analyze > Set Scale. The value is automatically imported here, however.
getPixelSize(unit, pixelWidth, pixelHeight);
s= 1/pixelWidth;
w= getWidth()
L= (w*sqrt(2))
x= getNumber("centroid x", 278);
y= getNumber("centroid y", 240);


	for (i=0; i<=360; i++)
	{	
		makeLine (x*s, y*s, ((L*cos(i*(PI/180)))+x*s), ((L*sin(i*(PI/180)))+y*s));
		b= getProfile();
		run("Set Measurements...", "integrated limit redirect=None decimal=0");
		run("Measure");
	}
	
