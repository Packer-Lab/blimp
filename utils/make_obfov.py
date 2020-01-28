import win32com.client
import time

# Start PrairieLink
pl = win32com.client.Dispatch('PrairieLink.Application')
print('object created')

# Connect to Client
pl.Connect()
print(pl.Connected)

pl.SendScriptCommands('-ROILoad noROI')  # clear previous ROI
time.sleep(2)
pl.SendScriptCommands('-EnterROI 0 0.25 1 0.5')