# Alien Effects for Alienware 13 R3 

All lights can be controlled via USB protocol.

For this specific device `vendor Id = 0x187c` and `product Id = 0x0529`

Commands can be passed using control transfers of USB protocol.

Alienware 13 R3 has 8 configurable light zones as listed in the table below.

## Terminology
**Sequence**: An ordered list of actions.

**Theme**: A set of sequences and corresponding zones.

## Control transfer: Write operation parameters

    bmRequestType = 0x21
        0... .... : Host to Device
        .01. .... : Request Type = Class
        ...0 0001 : Recipient = Interface
    bRequest = 9
    wValue = 0x0202
    wIndex = 0

## Control transfer: Read operation parameters

    bmRequestType = 0xa1
        1... .... : Device to Host
        .01. .... : Request Type = Class
        ...0 0001 : Recipient = Interface
    bRequest = 9
    wValue = 0x0202
    wIndex = 0

## Commands

| Command | Packet Structure (bytes) | Desciption | Comment | 
| -- | -- | -- | -- |
| Reset |  2 7 t 0 0 0 0 0 0 0 0 0 | t : type, t=3 : reset all off and stops the execution of sequences t=4 : reset all on | Should call before every change. This takes some time, and you should wait until the operation ends. Premature commands might fail.  
| Get status |  2 6 0 0 0 0 0 0 0 0 0 0 | S : Sequence ID, Z : Zone | Can use this to wait until status is ready | 
| Morph |  2 1 S Z Z Z r g b R G B | S : Sequence ID, Z : Zone | Color changes from `r g b` to `R G B` | 
| Pulse |  2 2 S Z Z Z r g b 0 0 0 | S : Sequence ID, Z : Zone |  | 
| Simple set |  2 3 S Z Z Z r g b 0 0 0 | S : Sequence ID, Z : Zone |  | 
| Loop |  2 4 0 0 0 0 0 0 0 0 0 0 | S : Sequence ID, Z : Zone | Without this, LEDs will go off after walking through the user-specified   color sequence. TODO: how does this know which sequence is the target? The last one mentioned? What happens if sequences are interleaved?) | 
| Execute |  2 5 0 0 0 0 0 0 0 0 0 0 | S : Sequence ID, Z : Zone | This must be called at the end. Start executing color sequences | 
| Save next command |  2 8 m 0 0 0 0 0 0 0 0 0 | m : mode, m=01: Initial State m=2: Plugged in - Sleep; Only the power-button works in this mode? m=5: Plugged in - Normal m=6: Plugged in - Charging m=7: On Battery - Sleep m=8: On Battery - Normal m=9: On Battery - Low | Save the next command to the specified mode. Must be followed by an Action or Loop | 
| Save all |  2 9 0 0 0 0 0 0 0 0 0 0 |  | Save slots permanently. If this command is not called, data slots will be lost on reboot |
| Time period/Tempo |  2 9 e t t 0 0 0 0 0 0 0 | t: time period | AlienFX sets this value between 00:1e ~ 03:ae. |


### 0x1C: Dim

    02:1C:oo:bb:  :  :  :  :

    o: 32 (Enable)
       64 (Disable)
    b: 01 (Always)
       00 (in Battery Mode Only)


### 0x1D: (Unknown)

    02:1d:03:  :  :  :  :  :   (on apply)
    02:1d:81:  :  :  :  :  :   (on go-dark)

# Reverse Engineering - Zone codes

* A 16 bit code space is to reference each light zone.
* One hot encoding is used; i.e. address for each zone has 1 at a unique place and 0's elsewhere
* Multiple zones can be addressed by ORing their codes
    * For example to address the entire keyboard use 0x1\|0x2\|0x4\|0x8=0xF code
* A lot more zone codes and command codes might exist, which can do things we dont know about (yet), 
    * For example setting multiple zones to different colors and such stuff

| Zone Alienware 13 R3 | Binary | Hex | 
| -- | -- | -- | 
| Keyboard right | 000 0000 0000 0001 | 0x0001 |
| Keyboard middle-right | 000 0000 0000 0010 | 0x0002 |
| Keyboard middle-left | 000 0000 0000 0100 | 0x0004 |
| Keyboard left | 000 0000 0000 1000 | 0x0008 |
| unknown/unused | 000 0000 0001 0000 | 0x0010 |
| Alien head | 000 0000 0010 0000 | 0x0020 |
| Alienware logo | 000 0000 0100 0000 | 0x0040 |
| Touch pad | 000 0000 1000 0000 | 0x0080 |
| Power button | 000 0001 0000 0000 | 0x0100 |

States: Some zone seem to be only be accessed in some states.
Caution: Different settings for a zone in different states may interfere, so that flashing can happen...

### References
[Alienfx](https://github.com/trackmastersteve/alienfx) by trackmastersteve
