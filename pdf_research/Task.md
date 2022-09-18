# Task for PDF research
Write a python script that takes in a url (e.g. `https://arxiv.org/pdf/1402.5127.pdf`) and outputs
- title: str (`Black holes and thermodynamics — The first half century`)
- authors: List (`["Daniel Grumiller", "Robert McNees", "Jakob Salzer"]`)
- abstract: str
```
Black hole thermodynamics emerged from the classical general relativistic laws of black hole mechanics, summarized by Bardeen–Carter–Hawking, together with the physical insights by Bekenstein about black hole entropy and the
semi-classical derivation by Hawking of black hole evaporation. The black hole
entropy law inspired the formulation of the holographic principle by ’t Hooft and
Susskind, which is famously realized in the gauge/gravity correspondence by Maldacena, Gubser–Klebanov–Polaykov and Witten within string theory. Moreover, the
microscopic derivation of black hole entropy, pioneered by Strominger–Vafa within
string theory, often serves as a consistency check for putative theories of quantum
gravity. In this book chapter we review these developments over five decades, starting in the 1960ies.
```
- tree of sections / table of contents (you can write a Tree data structure)
```
Black holes and thermodynamics - The first half century
|-- Introduction and Prehistory
|   |-- Introductory remarks.
|   |-- Prehistory.
|-- 1963-1973
|   |-- Black hole solutions and the uniqueness theorem.
|   |-- Penrose process and superradiant scattering.
... 
```
It should work on general PDFs, such as
- `https://arxiv.org/pdf/1402.5127.pdf`
- `https://arxiv.org/pdf/1901.06573.pdf`
- `https://arxiv.org/pdf/2204.00596.pdf`
if lucky the pdf already contains a table of contents. so yay. but if not try to find a way to extract it (usually headings are a different font size / are bolded)