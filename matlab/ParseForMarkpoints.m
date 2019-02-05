function Points = ParseForMarkpoints(Points, inputParameters)
%takes input of a points object and appends voltage fields requried by
%JR 2019 meat by LR 2018


% get values from settings file
yaml = ReadYaml('settings.yml'); 

% prairie numbers
ScanAmp_X           = yaml.ScanAmp_X;
ScanAmp_Y           = yaml.ScanAmp_Y;
FOVsize_OpticalZoom = yaml.FOVsize_OpticalZoom;
FOVsize_PX          = yaml.FOVsize_PX;
FOVsize_UM_1x       = yaml.FOVsize_UM_1x;


% convert full field into imaging FOV
ScanAmp_V_FOV_X = ((ScanAmp_X - mean(ScanAmp_X)) / FOVsize_OpticalZoom) + mean(ScanAmp_X);  % centre, scale, offset
ScanAmp_V_FOV_Y = ((ScanAmp_Y - mean(ScanAmp_Y)) / FOVsize_OpticalZoom) + mean(ScanAmp_Y);  % centre, scale, offset
 
 
% build LUT's
LUTx = linspace(ScanAmp_V_FOV_X(1), ScanAmp_V_FOV_X(2), FOVsize_PX);
LUTy = linspace(ScanAmp_V_FOV_Y(1), ScanAmp_V_FOV_Y(2), FOVsize_PX);
 
Xpx = Points.centroid_x;
Ypx = Points.centroid_y;


% convert pixel coordinates to voltages
Points.Xv = LUTx(Xpx+1);
Points.Yv = LUTy(Ypx+1);

% load the apl to get spiral size out
% weirld formatted string so have to spilt
gpl_struct = xml2struct(inputParameters.GPLpath);

ss = split(gpl_struct.PVGalvoPointList.PVGalvoPoint.Attributes.SpiralSize, ' ');
Points.SpiralSizeV = str2double(ss{1});
