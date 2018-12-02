Set oWMP = CreateObject("WMPlayer.OCX.7")
Set colCDROMs = oWMP.cdromCollection
For i = 0 to colCDROMs.Count-1
colCDROMs.Item(i).Eject
next
oWMP.close