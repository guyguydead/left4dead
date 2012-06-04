#include <sourcemod>

#define PLUGIN_VERSION "0.1"
#define MAX_LINE_WIDTH 64

// Cvar handles
new Handle:cvar_survival_stats = INVALID_HANDLE;

// Disable check Cvar handles
new Handle:cvar_Difficulty = INVALID_HANDLE;
new Handle:cvar_Gamemode = INVALID_HANDLE;
new Handle:cvar_Cheats = INVALID_HANDLE;

new hunters[MAXPLAYERS + 1]
new smokers[MAXPLAYERS + 1]
new boomers[MAXPLAYERS + 1]
new chargers[MAXPLAYERS + 1]
new jockeys[MAXPLAYERS + 1]
new spitters[MAXPLAYERS + 1]
new tanks[MAXPLAYERS + 1]

new start_tick = 0;
new end_tick = 0;

const TEAM_NONE       = 0;
const TEAM_SPECTATOR  = 1;
const TEAM_SURVIVOR   = 2;
const TEAM_INFECTED   = 3;

public Plugin:myinfo = 
{
	name = "Survival Stats Plugin",
	author = "guyguy",
	description = "Keeps track of kill counts within a survival round",
	version = PLUGIN_VERSION,
	url = "<- URL ->"
}

public OnPluginStart()
{
	CreateConVar("sm_survival_stats", "0", "Determines plugin functionality. (0 = Off, 1 = On)", true, 0.0, true, 1.0);
    CreateConVar("sm_survival_stats_version", PLUGIN_VERSION, "L4D Stats Version", FCVAR_PLUGIN|FCVAR_SPONLY|FCVAR_REPLICATED|FCVAR_NOTIFY|FCVAR_DONTRECORD);

    cvar_Difficulty = FindConVar("z_difficulty");
    cvar_Gamemode = FindConVar("mp_gamemode");
    cvar_Cheats = FindConVar("sv_cheats");

    HookEvent("player_death", event_PlayerDeath);
    HookEvent("survival_round_start", event_RoundStart);
    HookEvent("round_end", event_RoundEnd, EventHookMode_Pre);
	RegConsoleCmd("sm_survival_kills", Command_Kills);
	RegConsoleCmd("sm_sstats", Command_Kills);
}

// Reset all variables when a map changes.
public OnMapStart()
{
    ResetVars();
}

InvalidGameMode()
{
	/*
    new String:CurrentMode[16];
    GetConVarString(cvar_Gamemode, CurrentMode, sizeof(CurrentMode));

	// Search for survival in the gamemode. If not found, the mode is invalid.
    if (StrContains(CurrentMode, "survival", false) == -1)
        return true;
	*/

    return false;
}

StatsDisabled()
{
    if (InvalidGameMode())
        return true;

    if (GetConVarBool(cvar_Cheats))
        return true;

    return false;
}

ResetVars()
{
	start_tick = GetSysTickCount();
	end_tick = start_tick;

	for (new i = 0; i < MAXPLAYERS + 1; ++i)
	{
		hunters[i] = 0;
		smokers[i] = 0;
		boomers[i] = 0;
		chargers[i] = 0;
		jockeys[i] = 0;
		spitters[i] = 0;
		tanks[i] = 0;
	}
}

public Action:event_RoundStart(Handle:event, const String:name[], bool:dontBroadcast)
{
	ResetVars();
	return Plugin_Handled;
}

public Action:event_RoundEnd(Handle:event, const String:name[], bool:dontBroadcast)
{
	if (end_tick == start_tick)
		end_tick = GetSysTickCount();
}

public Action:event_PlayerDeath(Handle:event, const String:name[], bool:dontBroadcast)
{
    if (StatsDisabled())
		return Plugin_Handled;

    new Attacker = GetClientOfUserId(GetEventInt(event, "attacker"));

    if (GetEventBool(event, "attackerisbot") || !GetEventBool(event, "victimisbot"))
		return Plugin_Handled;

    decl String:AttackerID[MAX_LINE_WIDTH];
    GetClientAuthString(Attacker, AttackerID, sizeof(AttackerID));
    decl String:AttackerName[MAX_LINE_WIDTH];
    GetClientName(Attacker, AttackerName, sizeof(AttackerName));

	//Get the attacker from the event
	new attacker = GetClientOfUserId(GetEventInt(event, "attacker"));

	//Only process if the player is a legal attacker (i.e., a player)
	if (attacker && attacker <= MaxClients)
	{
		decl String:VictimName[MAX_LINE_WIDTH];
		GetEventString(event, "victimname", VictimName, sizeof(VictimName));

		if (StrEqual(VictimName, "Hunter"))
		{
			hunters[attacker]++;
		}
		else if (StrEqual(VictimName, "Smoker"))
		{
			smokers[attacker]++;
		}
		else if (StrEqual(VictimName, "Boomer"))
		{
			boomers[attacker]++;
		}
		else if (StrEqual(VictimName, "Charger"))
		{
			chargers[attacker]++;
		}
		else if (StrEqual(VictimName, "Jockey"))
		{
			jockeys[attacker]++;
		}
		else if (StrEqual(VictimName, "Spitter"))
		{
			spitters[attacker]++;
		}
		else if (StrEqual(VictimName, "Tank"))
		{
			tanks[attacker]++;
		}
	}
	return Plugin_Handled;
}

public Action:Command_Kills(client, args)
{
	decl String:g_sTemp[256];

	new Handle:g_hPanel = CreatePanel();
	SetPanelTitle(g_hPanel, "Kill Counter");
	DrawPanelText(g_hPanel, "============");

	// get the players
	GetPlayerString(g_sTemp, sizeof(g_sTemp));
	ReplyToCommand(client, g_sTemp);
	DrawPanelText(g_hPanel, g_sTemp);

	// print out the map name
	GetCurrentMap(g_sTemp, sizeof(g_sTemp));
	ReplyToCommand(client, g_sTemp);
	DrawPanelText(g_hPanel, g_sTemp);

	// print out the date
	FormatTime(g_sTemp, sizeof(g_sTemp), "%Y-%m-%d");
	ReplyToCommand(client, g_sTemp);
	DrawPanelText(g_hPanel, g_sTemp);

	// print out the time elapsed
	CalcTimeElapsedString(g_sTemp, sizeof(g_sTemp));
	ReplyToCommand(client, g_sTemp);
	DrawPanelText(g_hPanel, g_sTemp);

	// print out the kill counts
	ReplyToCommand(client, "============");

	Format(g_sTemp, sizeof(g_sTemp), "Hunter Kills: %d", hunters[client]);
	DrawPanelText(g_hPanel, g_sTemp);
	ReplyToCommand(client, g_sTemp);

	Format(g_sTemp, sizeof(g_sTemp), "Smoker Kills: %d", smokers[client]);
	DrawPanelText(g_hPanel, g_sTemp);
	ReplyToCommand(client, g_sTemp);

	Format(g_sTemp, sizeof(g_sTemp), "Boomer Kills: %d", boomers[client]);
	DrawPanelText(g_hPanel, g_sTemp);
	ReplyToCommand(client, g_sTemp);

	Format(g_sTemp, sizeof(g_sTemp), "Charger Kills: %d", chargers[client]);
	DrawPanelText(g_hPanel, g_sTemp);
	ReplyToCommand(client, g_sTemp);

	Format(g_sTemp, sizeof(g_sTemp), "Jockey Kills: %d", jockeys[client]);
	DrawPanelText(g_hPanel, g_sTemp);
	ReplyToCommand(client, g_sTemp);

	Format(g_sTemp, sizeof(g_sTemp), "Spitter Kills: %d", spitters[client]);
	DrawPanelText(g_hPanel, g_sTemp);
	ReplyToCommand(client, g_sTemp);

	Format(g_sTemp, sizeof(g_sTemp), "Tank Kills: %d", tanks[client]);
	DrawPanelText(g_hPanel, g_sTemp);
	ReplyToCommand(client, g_sTemp);
	DrawPanelText(g_hPanel, "============");
	ReplyToCommand(client, "============");
	CloseHandle(g_hPanel);

	SendPanelToClient(g_hPanel, client, PanelHandler1, 20);

	return Plugin_Handled;
}

public PanelHandler1(Handle:menu, MenuAction:action, param1, param2)
{
	//
}

CalcTimeElapsedString(String:buf[], length)
{
	new elapsed = end_tick - start_tick; // this is in milliseconds
	if (elapsed < 0)
		elapsed = -elapsed;

	new minutes = RoundToZero(RoundToZero((end_tick - start_tick) / 1000.0) / 60.0);
	new seconds = RoundToZero((end_tick - start_tick) / 1000.0) % 60;
	new milliseconds = (end_tick - start_tick) % 1000;

	Format(buf, length, "start: %d\nend: %d\n%d:%d.%d rounded: %d:%d.%d", start_tick, end_tick, minutes, seconds, milliseconds, minutes, seconds, RoundToNearest(milliseconds / 10.0));
}

GetPlayerString(String:buf[], length)
{
	decl String:tmp[256];
	new numplayers = 0;

	Format(buf, length, "");

	//Calculate who is on what team
	for (new i = 1; i <= MaxClients; i++)
	{
		if (IsClientConnected(i) && IsClientInGame(i))
		{
			new team = GetClientTeam(i);

			if (team == TEAM_SURVIVOR && !IsFakeClient(i))
			{
				if (numplayers > 0)
				{
					Format(tmp, sizeof(tmp), ", ");
					StrCat(buf, length, tmp);
				}

				GetClientName(i, tmp, sizeof(tmp));
				StrCat(buf, length, tmp);
				numplayers++;
			}
		}
	}
}

