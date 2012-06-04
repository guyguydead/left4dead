//
// Rotation For L4D2 Survival Maps
//


#include <sourcemod>
#include <sdktools>
new String:CurrentMap[128];
new String:NextMap[128];


public Plugin:myinfo = 
{
    name = "L4D2 Survival Map Rotation",
    author = "Sky",
    description = "survival rotation",
    version = "1.1",
};

public OnPluginStart()
{
	//HookEvent("survival_round_start", Survival_Round_Start);
	HookEvent("round_end", Round_End);
}

public Action:Round_End(Handle:event, const String:event_name[], bool:dontBroadcast)
{
	GetCurrentMap(CurrentMap, sizeof(CurrentMap));
	if (StrContains(CurrentMap, "c1m4_atrium", true))
	{
		NextMap = "c2m1_highway";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c2m1_highway", NextMap);
	}
	else if (StrContains(CurrentMap, "c2m1_highway", true))
	{
		NextMap = "c2m4_barns";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c2m4_barns", NextMap);
	}
	else if (StrContains(CurrentMap, "c2m4_barns", true))
	{
		NextMap = "c2m5_concert";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c2m5_concert", NextMap);
	}
	else if (StrContains(CurrentMap, "c2m5_concert", true))
	{
		NextMap = "c3m1_plankcountry";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c3m1_plankcountry", NextMap);
	}
	else if (StrContains(CurrentMap, "c3m1_plankcountry", true))
	{
		NextMap = "c3m4_plantation";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c3m4_plantation", NextMap);
	}
	else if (StrContains(CurrentMap, "c3m4_plantation", true))
	{
		NextMap = "c4m1_milltown_a";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c4m1_milltown_a", NextMap);
	}
	else if (StrContains(CurrentMap, "c4m1_milltown_a", true))
	{
		NextMap = "c4m2_milltown_b";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c4m2_milltown_b", NextMap);
	}
	else if (StrContains(CurrentMap, "c4m2_milltown_b", true))
	{
		NextMap = "c5m2_park";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c5m2_park", NextMap);
	}
	else if (StrContains(CurrentMap, "c5m2_park", true))
	{
		NextMap = "c5m5_bridge";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c5m5_bridge", NextMap);
	}
	else if (StrContains(CurrentMap, "c5m5_bridge", true))
	{
		NextMap = "c1m4_atrium";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c1m4_atrium", NextMap);
	}
	else
	{
		NextMap = "c1m4_atrium";
		PrintToChatAll("\x04Next Map: \x03 %s", NextMap);
		ServerCommand("changelevel c1m4_atrium", NextMap);
	}
}
