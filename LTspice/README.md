# Simulating with LTspice

For diodes we need only one additional model line in the lib/cmp/standard.dio file

Opamps are subcircuits. We need to add the *.sub file to lib/sub and the symbol file *.asy to the lib/sym/OpAmps folder.

## Add the components that are not included with LTspice

Find your C:\Users\YOUR_USERNAME\Documents\LTspiceXVII\lib\ folder.
In Linux with wine look in ~/.wine.

- Place the *.asy files in your "sym" folder
- Place the *.sub files in your "sub" folder.
- Place the diode file in your "cmp" folder (the old file is overridden).
- For the pot select "SPICE Directive" and paste in .include pot.sub.
- Restart LTspice

## Tips

ICL7660 is the same as LTC1044 already contained in LTspice.

## Problems

- MAX4128 does not work.


