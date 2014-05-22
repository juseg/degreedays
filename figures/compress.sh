#!/bin/bash

for f in *.pdf
  do ps2pdf $f ${f%.pdf}-compressed.pdf
  mv ${f%.pdf}-compressed.pdf $f
done
