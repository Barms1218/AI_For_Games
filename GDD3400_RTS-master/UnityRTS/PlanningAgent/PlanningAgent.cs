using System.Collections.Generic;
using System.Linq;
using GameManager.EnumTypes;
using GameManager.GameElements;
using UnityEngine;
using System;
using static UnityEngine.UI.GridLayoutGroup;
using System.Xml.Serialization;
using System.Net.Mail;

/////////////////////////////////////////////////////////////////////////////
// This is the Moron Agent
/////////////////////////////////////////////////////////////////////////////



namespace GameManager
{
    ///<summary>Planning Agent is the over-head planner that decided where
    /// individual units go and what tasks they perform.  Low-level 
    /// AI is handled by other classes (like pathfinding).
    ///</summary> 
    public class PlanningAgent : Agent
    {
        private const int DESIRED_WORKERS = 10;
        private const int MAX_BASES = 1;
        private const int MAX_BARRACKS = 2;
        private const int MAX_REFINERIES = 1;
        private const int DESIRED_SOLDIERS = 30;
        private const int DESIRED_ARCHERS = 30;
        private const int DESIRED_GOLD = 3000;

        #region Private Data

        ///////////////////////////////////////////////////////////////////////
        // Handy short-cuts for pulling all of the relevant data that you
        // might use for each decision.  Feel free to add your own.
        ///////////////////////////////////////////////////////////////////////
        ///
        private enum PlayerState
        {
            BuildBase = 0,
            BuildArmy = 1,
            ATTACK = 2
        }

        /// <summary>
        /// The enemy's agent number
        /// </summary>
        private int enemyAgentNbr { get; set; }

        /// <summary>
        /// My primary mine number
        /// </summary>
        private int mainMineNbr { get; set; }

        /// <summary>
        /// My primary base number
        /// </summary>
        private int mainBaseNbr { get; set; }

        /// <summary>
        /// List of all the mines on the map
        /// </summary>
        private List<int> mines { get; set; }

        /// <summary>
        /// List of all of my workers
        /// </summary>
        private List<int> myWorkers { get; set; }

        /// <summary>
        /// List of all of my soldiers
        /// </summary>
        private List<int> mySoldiers { get; set; }

        /// <summary>
        /// List of all of my archers
        /// </summary>
        private List<int> myArchers { get; set; }

        /// <summary>
        /// List of all of my bases
        /// </summary>
        private List<int> myBases { get; set; }

        /// <summary>
        /// List of all of my barracks
        /// </summary>
        private List<int> myBarracks { get; set; }

        /// <summary>
        /// List of all of my refineries
        /// </summary>
        private List<int> myRefineries { get; set; }

        /// <summary>
        /// List of the enemy's workers
        /// </summary>
        private List<int> enemyWorkers { get; set; }

        /// <summary>
        /// List of the enemy's soldiers
        /// </summary>
        private List<int> enemySoldiers { get; set; }

        /// <summary>
        /// List of enemy's archers
        /// </summary>
        private List<int> enemyArchers { get; set; }

        /// <summary>
        /// List of the enemy's bases
        /// </summary>
        private List<int> enemyBases { get; set; }

        /// <summary>
        /// List of the enemy's barracks
        /// </summary>
        private List<int> enemyBarracks { get; set; }

        /// <summary>
        /// List of the enemy's refineries
        /// </summary>
        private List<int> enemyRefineries { get; set; }

        /// <summary>
        /// List of the possible build positions for a 3x3 unit
        /// </summary>
        private List<Vector3Int> buildPositions { get; set; }

        private Dictionary<String, float> heuristics;

        /// <summary>
        /// The state that the player's forces are in.
        /// </summary>
        private PlayerState playerState;

        /// <summary>
        /// Finds all of the possible build locations for a specific UnitType.
        /// Currently, all structures are 3x3, so these positions can be reused
        /// for all structures (Base, Barracks, Refinery)
        /// Run this once at the beginning of the game and have a list of
        /// locations that you can use to reduce later computation.  When you
        /// need a location for a build-site, simply pull one off of this list,
        /// determine if it is still buildable, determine if you want to use it
        /// (perhaps it is too far away or too close or not close enough to a mine),
        /// and then simply remove it from the list and build on it!
        /// This method is called from the Awake() method to run only once at the
        /// beginning of the game.
        /// </summary>
        /// <param name="unitType">the type of unit you want to build</param>
        public void FindProspectiveBuildPositions(UnitType unitType)
        {
            // For the entire map
            for (int i = 0; i < GameManager.Instance.MapSize.x; ++i)
            {
                for (int j = 0; j < GameManager.Instance.MapSize.y; ++j)
                {
                    // Construct a new point near gridPosition
                    Vector3Int testGridPosition = new Vector3Int(i, j, 0);

                    // Test if that position can be used to build the unit
                    if (Utility.IsValidGridLocation(testGridPosition)
                        && GameManager.Instance.IsBoundedAreaBuildable(unitType, testGridPosition))
                    {
                        // If this position is buildable, add it to the list
                        buildPositions.Add(testGridPosition);
                    }
                }
            }
        }

        /// <summary>
        /// Build a building
        /// </summary>
        /// <param name="unitType"></param>
        public void BuildBuilding(UnitType unitType)
        {
            // For each worker
            foreach (int worker in myWorkers)
            {
                buildPositions = buildPositions.OrderBy(pos => Vector3Int.Distance(pos, GameManager.Instance.GetUnit(mainMineNbr).GridPosition)).ToList();

                // Grab the unit we need for this function
                Unit unit = GameManager.Instance.GetUnit(worker);

                // Make sure this unit actually exists and we have enough gold
                if (unit != null && Gold >= Constants.COST[unitType])
                {
                    // Find the closest build position to this worker's position (DUMB) and 
                    // build the base there
                    foreach (Vector3Int toBuild in buildPositions)
                    {
                        if (GameManager.Instance.IsBoundedAreaBuildable(unitType, toBuild))
                        {
                            Build(unit, toBuild, unitType);
                            return;
                        }
                    }
                }
            }
        }


        /// <summary>
        /// Attack the enemy
        /// </summary>
        /// <param name="myTroops"></param>
        public void AttackEnemy(List<int> myTroops)
        {
            // For each of my troops in this collection
            foreach (int troopNbr in myTroops)
            {
                // If this troop is idle, give him something to attack
                Unit troopUnit = GameManager.Instance.GetUnit(troopNbr);

                if (troopUnit.CurrentAction == UnitAction.IDLE)
                {

                    // If there are soldiers to attack
                    if (heuristics.Values.Max() == heuristics["Attack Soldiers"])
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemySoldiers[UnityEngine.Random.Range(0, enemySoldiers.Count)]));
                    }
                    // If there are archers to attack and no soldiers
                    else if (heuristics.Values.Max() == heuristics["Attack Archers"])
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyArchers[UnityEngine.Random.Range(0, enemyArchers.Count)]));
                    }
                    // If there are workers to attack
                    else if (heuristics.Values.Max() == heuristics["Attack Workers"])
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyWorkers[UnityEngine.Random.Range(0, enemyWorkers.Count)]));
                    }
                    // If there are barracks to attack
                    else if (heuristics.Values.Max() == heuristics["Attack Barracks"])
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyBarracks[UnityEngine.Random.Range(0, enemyBarracks.Count)]));
                    }
                    // If there are bases to attack
                    else if (heuristics.Values.Max() == heuristics["Attack Bases"])
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyBases[UnityEngine.Random.Range(0, enemyBases.Count)]));
                    }
                    // If there are refineries to attack
                    else if (heuristics.Values.Max() == heuristics["Attack Refineries"])
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyRefineries[UnityEngine.Random.Range(0, enemyRefineries.Count)]));
                    }
                }
            } 
        }
        #endregion

        #region Public Methods

        /// <summary>
        /// Called at the end of each round before remaining units are
        /// destroyed to allow the agent to observe the "win/loss" state
        /// </summary>
        public override void Learn()
        {
            Debug.Log("Nbr Wins: " + AgentNbrWins);

            //Debug.Log("PlanningAgent::Learn");
            Log("value 1");
            Log("value 2");
            Log("value 3a, 3b");
            Log("value 4");
        }

        /// <summary>
        /// Called before each match between two agents.  Matches have
        /// multiple rounds. 
        /// </summary>
        public override void InitializeMatch()
        {
            Debug.Log("My change works.");
            Debug.Log("Branden's: " + AgentName);
            Debug.Log(playerState.ToString());
            //Debug.Log("PlanningAgent::InitializeMatch");
        }

        /// <summary>
        /// Called at the beginning of each round in a match.
        /// There are multiple rounds in a single match between two agents.
        /// </summary>
        public override void InitializeRound()
        {
            //Debug.Log("PlanningAgent::InitializeRound");
            buildPositions = new List<Vector3Int>();

            FindProspectiveBuildPositions(UnitType.BASE);

            // Initialize the heuristics
            heuristics = new Dictionary<String, float>()
            {
                {"Build Base", 0f },
                {"Build Barracks", 0f },
                {"Build Refinery", 0f },
                {"Train Worker", 0f },
                {"Train Soldier", 0f },
                {"Train Archer", 0f },
                {"Gather Gold", 0f },
                {"Attack Archers", 0f },
                {"Attack Soldiers", 0f },
                {"Attack Workers", 0f },
                {"Attack Bases", 0f },
                {"Attack Barracks", 0f },
                {"Attack Refineries", 0f }
            };
            // Set the main mine and base to "non-existent"
            mainMineNbr = -1;
            mainBaseNbr = -1;

            // Initialize all of the unit lists
            mines = new List<int>();
            mines = GameManager.Instance.GetUnitNbrsOfType(UnitType.MINE, AgentNbr);

            myWorkers = new List<int>();
            mySoldiers = new List<int>();
            myArchers = new List<int>();
            myBases = new List<int>();
            myBarracks = new List<int>();
            myRefineries = new List<int>();

            enemyWorkers = new List<int>();
            enemySoldiers = new List<int>();
            enemyArchers = new List<int>();
            enemyBases = new List<int>();
            enemyBarracks = new List<int>();
            enemyRefineries = new List<int>();

            playerState = PlayerState.BuildBase;
        }

        /// <summary>
        /// Updates the game state for the Agent - called once per frame for GameManager
        /// Pulls all of the agents from the game and identifies who they belong to
        /// </summary>
        public void UpdateGameState()
        {
            // Update the common resources
            mines = GameManager.Instance.GetUnitNbrsOfType(UnitType.MINE);

            // Update all of my unitNbrs
            myWorkers = GameManager.Instance.GetUnitNbrsOfType(UnitType.WORKER, AgentNbr);
            mySoldiers = GameManager.Instance.GetUnitNbrsOfType(UnitType.SOLDIER, AgentNbr);
            myArchers = GameManager.Instance.GetUnitNbrsOfType(UnitType.ARCHER, AgentNbr);
            myBarracks = GameManager.Instance.GetUnitNbrsOfType(UnitType.BARRACKS, AgentNbr);
            myBases = GameManager.Instance.GetUnitNbrsOfType(UnitType.BASE, AgentNbr);
            myRefineries = GameManager.Instance.GetUnitNbrsOfType(UnitType.REFINERY, AgentNbr);

            Debug.Log("Player State is: " + playerState);

            // Update the enemy agents & unitNbrs
            List<int> enemyAgentNbrs = GameManager.Instance.GetEnemyAgentNbrs(AgentNbr);
            if (enemyAgentNbrs.Any())
            {
                enemyAgentNbr = enemyAgentNbrs[0];
                enemyWorkers = GameManager.Instance.GetUnitNbrsOfType(UnitType.WORKER, enemyAgentNbr);
                enemySoldiers = GameManager.Instance.GetUnitNbrsOfType(UnitType.SOLDIER, enemyAgentNbr);
                enemyArchers = GameManager.Instance.GetUnitNbrsOfType(UnitType.ARCHER, enemyAgentNbr);
                enemyBarracks = GameManager.Instance.GetUnitNbrsOfType(UnitType.BARRACKS, enemyAgentNbr);
                enemyBases = GameManager.Instance.GetUnitNbrsOfType(UnitType.BASE, enemyAgentNbr);
                enemyRefineries = GameManager.Instance.GetUnitNbrsOfType(UnitType.REFINERY, enemyAgentNbr);
                Debug.Log("<color=red>Enemy gold</color>: " + GameManager.Instance.GetAgent(enemyAgentNbr).Gold);
            }
        }

        /// <summary>
        /// Update the GameManager - called once per frame
        /// </summary>
        public override void Update()
        {
            UpdateGameState();

            CalculateHeuristics();


            if (mines.Count > 0)
            {
                mainMineNbr = mines[0];
            }
            else
            {
                mainMineNbr = -1;
            }

            switch (playerState)
            {
                case PlayerState.BuildBase:
                    // If we have at least one base, assume the first one is our "main" base
                    if (myBases.Count > 0)
                    {
                        mainBaseNbr = myBases[0];
                        Debug.Log("BaseNbr " + mainBaseNbr);
                        Debug.Log("MineNbr " + mainMineNbr);
                    }

                    if (heuristics["Build Base"] > 0.5f)
                    {
                        Debug.Log("BUILD BASE HEURISTIC IS:" + heuristics["Build Base"]);
                        mainBaseNbr += 1;
                        BuildBuilding(UnitType.BASE);
                    }
                    else if (heuristics["Build Barracks"] > 0.5f)
                    {
                        Debug.Log("BUILD BASE HEURISTIC IS:" + heuristics["Build Base"]);
                        BuildBuilding(UnitType.BARRACKS);
                    }
                    else if (heuristics["Build Refinery"] > 0.5f)
                    {
                        Debug.Log("BUILD BARRACKS HEURISTIC IS:" + heuristics["Build Barracks"]);
                        BuildBuilding(UnitType.REFINERY);
                    }
                    else if (heuristics["Train Worker"] > 0.5f)
                    {
                        TrainWorkers();
                    }
                    else if (heuristics["Gather Gold"] > 0.5f)
                    {
                        GatherGold(heuristics["Gather Gold"]);
                    }


                    if (myRefineries.Count >= MAX_REFINERIES && myBarracks.Count >= MAX_BARRACKS)
                    {
                        Debug.Log("CHANGING PLAYER STATE TO BUILD ARMY!!!!");
                        playerState = PlayerState.BuildArmy;
                    }

                    //TrainWorkers();
                    break;
                case PlayerState.BuildArmy:

                    // Build a second barracks so my army grows faster
                    if (myBarracks.Count < 2)
                    {
                        BuildBuilding(UnitType.BARRACKS);
                    }
                    if (heuristics["Train Archer"] > 0.5f)
                    {
                        TrainArchers();
                    }
                    else if (heuristics["Train Soldier"] > 0.5f)
                    {
                        TrainSoldiers();
                    }
                    else if (heuristics["Gather Gold"] > 0.5f)
                    {
                        GatherGold(heuristics["Gather Gold"]);
                    }

                    if (mySoldiers.Count >= DESIRED_SOLDIERS && myArchers.Count >= DESIRED_ARCHERS)
                    {
                        playerState = PlayerState.ATTACK;
                    }
                    else if (myWorkers.Count < 3)
                    {
                        playerState = PlayerState.BuildBase;
                    }
                    break;
                case PlayerState.ATTACK:
                    // Make more workers to rev up economy
                    if (heuristics["Train Worker"] > 0.5f)
                    {
                        TrainWorkers();
                    }
                    if (heuristics["Train Archer"] > 0.5f)
                    {
                        TrainArchers();
                    }
                    else if (heuristics["Train Soldier"] > 0.5f)
                    {
                        TrainSoldiers();
                    }
                    else if (heuristics["Gather Gold"] > 0.5f)
                    {
                        GatherGold(heuristics["Gather Gold"]);
                    }
                    // For any troops, attack the enemy
                    AttackEnemy(mySoldiers);
                    AttackEnemy(myArchers);

                    // Go back to building soldiers/archers
                    if (mySoldiers.Count + myArchers.Count < 3)
                    {
                        playerState = PlayerState.BuildArmy;
                    }
                    break;

            }
        }

        private void CalculateHeuristics()
        {
            // If there is less than one base, it is vital to build a base
            heuristics["Build Base"] = Mathf.Clamp(MAX_BASES - myBases.Count / MAX_BASES, 0, 1) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.BASE] - 1), 0, 1);
            // Build barracks
            heuristics["Build Barracks"] = Mathf.Clamp((MAX_BARRACKS - myBarracks.Count) / MAX_BARRACKS, 0, 1) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.BARRACKS] - 1), 0, 1);
            // Refineries are least important, max value is less to match
            heuristics["Build Refinery"] = Mathf.Clamp((MAX_REFINERIES - myRefineries.Count) / MAX_REFINERIES, 0, 1) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.REFINERY] - 1), 0, 1f);
            heuristics["Train Worker"] = Convert.ToInt32(playerState == PlayerState.BuildBase) *
                (myWorkers.Count / (2 * enemyWorkers.Count + myWorkers.Count)) -
                Convert.ToInt32(playerState == PlayerState.ATTACK) * myWorkers.Count / (DESIRED_WORKERS + 1);
            heuristics["Train Soldier"] = Mathf.Clamp(DESIRED_SOLDIERS - mySoldiers.Count, 0, 1) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.SOLDIER] - 1), 0, 1);
            // Train archers if not at the max
            heuristics["Train Archer"] = Mathf.Clamp(DESIRED_ARCHERS - myArchers.Count, 0, 1) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.ARCHER] - 1), 0, 1);
            // Gather gold if it's below the desired amount. More urgent as gold gets low
            heuristics["Gather Gold"] = Mathf.Clamp((DESIRED_GOLD - Gold) / DESIRED_GOLD, 0, 1);
            // kill soldiers while there are any soldiers
            heuristics["Attack Soldiers"] = Mathf.Clamp(0.5f * (1.0f - (enemySoldiers.Count / Mathf.Max(1, enemySoldiers.Count))), 0, 1f);
            // Kill archers while there are archers to kill
            heuristics["Attack Archers"] = Mathf.Clamp(0.5f * (1.0f - (enemyArchers.Count / Mathf.Max(1, enemyArchers.Count))), 0f, 1f);
            // Kill workers while there are workers to kill. Lower maximum priority than enemy troops.
            heuristics["Attack Workers"] = Mathf.Clamp(0.5f * (1.0f - (enemyWorkers.Count / Mathf.Max(1, enemyWorkers.Count))), 0f, 1f);
            // Attack enemy Bases
            heuristics["Attack Bases"] = Mathf.Clamp(0.9f * (1.0f - (enemyBases.Count / Mathf.Max(1, enemyBases.Count))), 0f, 0.9f);
            // Attack enemy Barracks
            heuristics["Attack Barracks"] = Mathf.Clamp(0.5f * (1.0f - (enemyBases.Count / Mathf.Max(1, enemyBases.Count))), 0f, 1f);
            // Attack enemy Refineries
            heuristics["Attack Refineries"] = Mathf.Clamp(0.5f * (1.0f - (enemyBases.Count / Mathf.Max(1, enemyBases.Count))), 0f, 0.5f);
        }

        private void GatherGold(float choice)
        {
            // For each worker
            foreach (int worker in myWorkers)
            {
                // Grab the unit we need for this function
                Unit unit = GameManager.Instance.GetUnit(worker);

                // Workers will look for the closest mine every state update
                if (myWorkers.Count > 0)
                {
                    FindClosestMine(unit);
                }

                // Make sure this unit actually exists and is idle
                if (unit != null && unit.CurrentAction == UnitAction.IDLE && mainBaseNbr >= 0 && mainMineNbr >= 0)
                {
                    // Grab the mine
                    Unit mineUnit = GameManager.Instance.GetUnit(mainMineNbr);
                    Unit baseUnit = GameManager.Instance.GetUnit(mainBaseNbr);
                    if (mineUnit != null && baseUnit != null && mineUnit.Health > 0)
                    {
                        Gather(unit, mineUnit, baseUnit);
                    }
                }
            }
        }

        private void TrainWorkers()
        {
            foreach (int baseNbr in myBases)
            {
                // Get the base unit
                Unit baseUnit = GameManager.Instance.GetUnit(baseNbr);

                // If the base exists, is idle, we need a worker, and we have gold
                if (baseUnit != null && baseUnit.IsBuilt
                                     && baseUnit.CurrentAction == UnitAction.IDLE
                                     && Gold >= Constants.COST[UnitType.WORKER])
                {
                    Train(baseUnit, UnitType.WORKER);
                }
            }
        }

        private void TrainSoldiers()
        {
            // For each barracks, determine if it should train a soldier or an archer
            foreach (int barracksNbr in myBarracks)
            {
                int soldierChance = UnityEngine.Random.Range(0, 100);

                // Get the barracks
                Unit barracksUnit = GameManager.Instance.GetUnit(barracksNbr);
                
                // If this barracks still exists, is idle, we need soldiers, and have gold
                if (barracksUnit != null && barracksUnit.IsBuilt
                    && barracksUnit.CurrentAction == UnitAction.IDLE
                    && Gold >= Constants.COST[UnitType.SOLDIER]
                    && soldierChance > 60)
                {
                    Train(barracksUnit, UnitType.SOLDIER);
                }
            }
        }

        private void TrainArchers()
        {
            foreach (int barracksNbr in myBarracks)
            {
                int soldierChance = UnityEngine.Random.Range(0, 100);

                // Get the barracks
                Unit barracksUnit = GameManager.Instance.GetUnit(barracksNbr);

                // If this barracks still exists, is idle, we need archers, and have gold
                if (barracksUnit != null && barracksUnit.IsBuilt
                         && barracksUnit.CurrentAction == UnitAction.IDLE
                         && Gold >= Constants.COST[UnitType.ARCHER]
                         && soldierChance <= 60)
                {
                    Train(barracksUnit, UnitType.ARCHER);
                }
            }
        }

        #endregion

        #region Private Methods

        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        private void FindClosestMine(Unit worker)
        {
            
            if (worker != null)
            {
                foreach (int mine in mines)
                {
                    mines = mines.OrderBy(pos => Vector3Int.Distance(worker.GridPosition, GameManager.Instance.GetUnit(mine).GridPosition)).ToList();
                }
            }
        }

        #endregion
    }
}