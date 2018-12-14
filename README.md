# Alienware 13 R3 lights protocol

## Terminology
**Zone**: A (or a set of) LED which share a sequence.
**Effect**: The lighting behavior for zones. Ex. Morph, Pulse, and Color.
**Sequence**: An ordered list of actions.
**Theme**: A set of sequences and corresponding zones.
##Device Configuration

use configuration 1. occasionally, kernel drivers need to be disabled


##URB Setup

### Sending

 - bmRequestType = 0x21

        0... .... : Host to Device
        .01. .... : Request Type = Class
        ...0 0001 : Recipient = Interface

 - bRequest = 9 (Constant)
 - wValue = 0x0202 (Constant)
 - wIndex = 0 (Constant)
 - wLength = 9 (Constant. Smaller message must be padded with 0)


### Receiving

 - bmRequestType = 0xa1  

        1... .... : Device to Host
        .01. .... : Request Type = Class
        ...0 0001 : Recipient = Interface

 - bRequest = 9 (Constant)
 - wValue = 0x0202 (Constant)
 - wIndex = 0 (Constant)
 - wLength = 9 (Constant)


### (Unkown)

 - AFAIK, not sending this packet does no harm.
 - bmRequestType = 0x21
 - bRequest = 10
 - wValue = 0 (Constant)
 - wIndex = 0 (Constant)
 - wLength = 0 (Constant)


## Commands

| Command | Packet Structure (bytes) | Desciption | Comment | 
| -- | -- | -- | -- |
| Reset |  2 7 t 0 0 0 0 0 0 0 0 0 | t : type | Should call before every change. This takes some time, and you should wait until the operation ends. Premature commands might fail. |
| Get status |  2 6 0 0 0 0 0 0 0 0 0 0 | S : Sequence ID, Z : Zone | Can use this to wait until status is ready | 
| Morph |  2 1 S Z Z Z r g b R G B | S : Sequence ID, Z : Zone | Color changes from `r g b` to `R G B` | 
| Pulse |  2 2 S Z Z Z r g b 0 0 0 | S : Sequence ID, Z : Zone |  | 
| Simple set |  2 3 S Z Z Z r g b 0 0 0 | S : Sequence ID, Z : Zone |  | 
| Loop |  2 4 0 0 0 0 0 0 0 0 0 0 | S : Sequence ID, Z : Zone | Without this, LEDs will go off after walking through the user-specified   color sequence. TODO: how does this know which sequence is the target? The last one mentioned? What happens if sequences are interleaved?) | 
| Execute |  2 5 0 0 0 0 0 0 0 0 0 0 | S : Sequence ID, Z : Zone | This must be called at the end. Start executing color sequences | 
| Save next command |  2 8 s 0 0 0 0 0 0 0 0 0 | s : slot | Save the next command to the specified slot. Must be followed by an Action or Loop | 
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

# Reverse Engineering

## Zone addresses:

It looks like, they used one bit per zone, so that we are able to set multiple zones by adding their base codes (as for keyboard 0xF)

There are a lot more zone-codes and command-codes which are doing things we dont know about (yet), 
like, for example setting multiple zones to different colors and such stuff, I think that these are used (or can be used) by some games.

| Hex | Binary | Zone Alienware 13 R3 | 
| -- | -- | -- | 
| 0x0001 | 000 0000 0000 0001 | Keyboard right
| 0x0002 | 000 0000 0000 0010 | Keyboard middle-right
| 0x0004 | 000 0000 0000 0100 | Keyboard middle-left
| 0x0008 | 000 0000 0000 1000 | Keyboard left
| 0x000F | 000 0000 0000 1111 | Keyboard: all fields <= interesting: 0x1 + 0x2 + 0x4 + 0x8 = 0xF

| 0x0010 | 000 0000 0001 0000 | unknown/unused

| 0x0020 | 000 0000 0010 0000 | Alien head
| 0x0040 | 000 0000 0100 0000 | Alienware name
| 0x0080 | 000 0000 1000 0000 | Touch pad
| 0x0100 | 000 0001 0000 0000 | Power button

| 0x0200 | 000 0010 0000 0000 | unknown/unused

States: Some zone seem to be only be accessed in some states.
Caution: Different settings for a zone in different states may interfere, so that flashing can happen...


### Reset

 - (TODO: tbh, this section, entirely)
 - 00: reset keyboard
 - 01: reset keyboard
 - 02: (TODO)
 - 03: reset all
       this also stops the execution of sequences
 - 04: (TODO)


### Slots

 - 01: Initial State
 - 02: Plugged in - Sleep
   + Only the power-button works in this mode?
 - 05: Plugged in - Normal
 - 06: Plugged in - Charging
 - 07: On Battery - Sleep
 - 08: On Battery - Normal
 - 09: On Battery - Low
 - (TODO: better title)

