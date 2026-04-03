---
layout: default
title: "File Analysis"
parent: "Misc"
grand_parent: "Defensive Security"
nav_order: 3
---


`Oledump.py` is a Python tool that analyzes **OLE2** files, commonly called Structured Storage or Compound File Binary Format. **OLE** stands for **Object Linking and Embedding,** a proprietary technology developed by Microsoft. OLE2 files are typically used to store multiple data types, such as documents, spreadsheets, and presentations, within a single file. This tool is handy for extracting and examining the contents of OLE2 files, making it a valuable resource for forensic analysis and malware detection.
- `oledump.py $file`
- then `oledump.py $file -s $treamNumber`
- then `oledump.py $file -s $treamNumber --vbadecompress`