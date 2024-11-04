import time;
import calendar

cal=calendar.month(2024,11)
localtime= time.asctime(time.localtime (time.time()))

print( """ 
_____________________\n|\n|Today's Date is 🌍\n_____
""",'⏰', localtime, '\n|\n_____Calender📜________\n|',cal,'\n|_____________________')
