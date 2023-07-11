# 3Dmigoto-Tailor

This tool is used in 3Dmigoto dump files which use higher vertex buffer slot,
for example some game only use vb0 to store all information like {Dead or Alive},
but other games use vb0,vb1,vb2,etc..,Unity game normally use vb0 to store POSITION,NORMAL,TANGENT info,
use vb1 to store COLOR,TEXCOORD info ,use vb2 to store BLENDWEIGHT or BLENDWEIGHTS, BLENDINDICES info,
and for UE4 it's more complicated,so if you need to use 3Dmigoto-Blender plugin from DarkStarSword's github
to import these dump file into blender, you will need to first merge these vb0,vb1,vb2 into a single vb0,
that is why I created 3Dmigoto-Tailor to do this,because manually do this will take a lot of time.

And 3Dmigoto-Tailor is designed to compatible with as many games as it can,so it's a little bit complicated
to use,but if you have some patient to read the code,you will know this tool can save a lot of time for you,
and is very simple to use once you understand the config file architecture.

But use 3Dmigoto to mod game is only restricted on GPU Driven Animation Game,so only part of the games 
can use 3Dmigoto, and most of them use Higher buffer slot tech,and Tailor can handle this.

Below is a list for the game that Tailor can process.

# Design
 - One time only extract one Index Buffer, because only process one is already easy to get error,
more than one part will be very hard to debug, I have test it a long time before,seems not good, so only
process one IB in one time.
 - After .ini file generated, you need to manually modify it to let it work well,because what generate is
just a example .ini file, not the final .ini file, you need to modify it yourself.
 - Now only support R16_UINT,but other similar project like GIMI,SRMI use R32_UINT to support more
vertex ,I have a plan to upgrade to R32_UINT,but maybe later,R16_UINT is enough to use now.
So here is a little problem,you have to use DarkStarSword's blend-3dmigoto plugin instead of
GIMI or SRMI's blender plugin,because their export .ib file is R32_UINT,you can also manually
modify the final generated .ini file to set it to R32_UINT so that you can use GIMI or SRMI's plugin.
 - TODO: TANGENT problem, TANGENT value is not the real TANGENT value in Unity game,so it need to be fix,
currently in Tailor there is only a simple fix copied from GIMI,and we need a complete fix method 
in the future.
see: https://github.com/SilentNightSound/GI-Model-Importer/pull/84

# GPU Driven Animation Games
 - Honkai Impact 3 崩坏三 
 - Honkai Star Rail 崩坏:星穹铁道 
 - Genshen Impact 原神 
 - Naraka Bladepoint 永劫无间 
 - Kena Bridge Of Spirit 科娜:精神之桥 
 - KALABIYAU 卡拉比丘(测试服) 
 - BLUE PROTOCOLS 蓝色协议

# Community

https://discord.gg/66gdwW8NWC

Join this discord for:

1.Technique support

2.bug-report

3.advice and feedback

4.Other



