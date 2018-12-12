Reverse-Engineering-Knowledgebase:
##################################

Zone addresses:
+++++++++++++++

NOTICE:
It seems that the alienfx-controllers are using doubles for base zone addresses.
Keep an eye on the binary-representation of the values in the following table:
It looks like, they used one bit per zone, so that we are able to set multiple zones by adding their base codes (as for keyboard 0xF)

There are a lot more zone-codes and command-codes which are doing things we dont know about (yet), 
like, for example setting multiple zones to different colors and such stuff.
i think that these are used (or can be used) by some games.

Zone addresses seem to follow the following pattern:

HEX    | Binary          | Zone on AW17R4
=========================================================================================
0x0001 | 000 0000 0000 0001 | Keyboard right
0x0002 | 000 0000 0000 0010 | Keyboard middle-right
0x0004 | 000 0000 0000 0100 | Keyboard middle-left
0x0008 | 000 0000 0000 1000 | Keyboard left
0x000F | 000 0000 0000 1111 | Keyboard: all fields <= interesting: 0x1 + 0x2 + 0x4 + 0x8 = 0xF

0x0010 | 000 0000 0001 0000 | unknown/unused

0x0020 | 000 0000 0010 0000 | Alien head
0x0040 | 000 0000 0100 0000 | Alienware name
0x0080 | 000 0000 1000 0000 | Touch pad
0x0100 | 000 0001 0000 0000 | Power button

0x0200 | 000 0010 0000 0000 | unknown/unused

0x0400 | 000 0100 0000 0000 | bottom (speaker) left
0x0800 | 000 1000 0000 0000 | bottom (speaker) right
0x1000 | 001 0000 0000 0000 | top (display) left
0x2000 | 010 0000 0000 0000 | top (display) right
0x4000 | 100 0000 0000 0000 | keyboard macrokey-bar (left)


States
+++++++
States: Some zone seem to be only be accessed in some states.
Caution: different settings for a zone in different states may interfere, so that flashing can happen...