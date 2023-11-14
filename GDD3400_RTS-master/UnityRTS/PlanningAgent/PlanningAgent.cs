﻿using System.Collections.Generic;
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
        private const float DESIRED_WORKERS = 10;
        private const float MAX_BASES = 1;
        private const float MAX_BARRACKS = 5;
        private const float MAX_REFINERIES = 1;
        private const float DESIRED_SOLDIERS = 30;
        private const float DESIRED_ARCHERS = 20;
        private const float DESIRED_GOLD = 3000;

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
        /// <param name="enemies"></param>
        public void AttackEnemy(List<int> myTroops, List<int> enemies)
        {
            // For each of my troops in this collection
            foreach (int troopNbr in myTroops)
            {
                // If this troop is idle, give him something to attack
                Unit troopUnit = GameManager.Instance.GetUnit(troopNbr);

                if (troopUnit.CurrentAction == UnitAction.IDLE && enemies.Count > 0)
                {
                    Attack(troopUnit, GameManager.Instance.GetUnit(enemies[UnityEngine.Random.Range(0, enemies.Count)]));
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
                {"Gather Gold", 0f },
                {"Build Base", 0f },
                {"Train Worker", 0f },
                {"Build Barracks", 0f },
                {"Build Refinery", 0f },
                {"Train Soldier", 0f },
                {"Train Archer", 0f },
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

            // Pick the first base built as your main base
            if (myBases.Count > 0)
            {
                mainBaseNbr = myBases[0];
            }
            // Pick the main mine for your faction
            if (mainMineNbr == -1 && mines.Count > 0 && myWorkers.Count > 0)
            {
                mainMineNbr = FindClosestMineToWorker(myWorkers[0]);
            }
            else
            {
                mainMineNbr = -1;
            }

            // Heuristic calculations handled in separate method because it's cleaner.
            CalculateHeuristics();

            // How the agents decide to change states.
            if (myBarracks.Count + myRefineries.Count > 0)
            {
                playerState = PlayerState.BuildArmy;
            }
            else if (mySoldiers.Count + myArchers.Count >= 20)
            {
                playerState = PlayerState.ATTACK;
            }


            Debug.LogWarning(playerState.ToString());


            foreach (KeyValuePair<String, float> item in heuristics)
            {
                if (item.Value > 0.25f)
                {
                    Debug.LogWarning("ACTION: " + item + " AND ITS VALUE IS: " + item.Value);
                    Debug.LogWarning(((DESIRED_WORKERS - myWorkers.Count) / DESIRED_WORKERS));
                    DoThing(item.Key);
                }
            }
        }

        /// <summary>
        /// A method that takes a value and has the agents do the appropriate action based 
        /// on it.
        /// </summary>
        /// <param name="value"></param>
        private void DoThing(string value)
        {
            switch (value)
            {
                case "Build Base":
                    BuildBuilding(UnitType.BASE);
                    break;
                case "Gather Gold":
                    GatherGold();
                    break;
                case "Train Worker":
                    TrainWorkers();
                    break;
                case "Build Barracks":
                    BuildBuilding(UnitType.BARRACKS);
                    break;
                case "Build Refinery":
                    BuildBuilding(UnitType.REFINERY);
                    break;
                case "Train Soldier":
                    TrainSoldiers();
                    break;
                case "Train Archer":
                    TrainArchers();
                    break;
                case "Attack Soldier":
                    AttackEnemy(mySoldiers, enemySoldiers);
                    AttackEnemy(myArchers, enemySoldiers);
                    break;
                case "Attack Archer":
                    AttackEnemy(mySoldiers, enemyArchers);
                    AttackEnemy(myArchers, enemyArchers);
                    break;
                case "Attack Worker":
                    AttackEnemy(mySoldiers, enemyWorkers);
                    AttackEnemy(myArchers, enemyWorkers);
                    break;
                case "Attack Base":
                    AttackEnemy(mySoldiers, enemyBases);
                    AttackEnemy(myArchers, enemyBases);
                    break;
                case "Attack Barracks":
                    AttackEnemy(mySoldiers, enemyBarracks);
                    AttackEnemy(myArchers, enemyBarracks);
                    break;
                case "Attack Refinery":
                    AttackEnemy(mySoldiers, enemyRefineries);
                    AttackEnemy(myArchers, enemyRefineries);
                    break;
            }
        }

        /// <summary>
        /// How the actions are calculated
        /// State-Based calculations done as part of the heuristics calculations
        /// </summary>
        private void CalculateHeuristics()
        {
            // State-Based Values. Gold and Bases not included because those are top priority always.
            float trainWorkerValue = playerState == PlayerState.BuildBase ? 1.0f : 0.75f;
            float trainSoldierValue = playerState == PlayerState.BuildArmy ? 1.0f : 0.7f;
            float trainArcherValue = playerState == PlayerState.BuildArmy ? 1.0f : 0.6f;
            float buildBarracksValue = playerState == PlayerState.BuildBase || playerState == PlayerState.BuildArmy ? 1.0f : 0.75f;
            float buildRefineryValue = playerState == PlayerState.BuildBase || playerState == PlayerState.ATTACK ? 1.0f : 0.5f;
            float attackBases = playerState == PlayerState.ATTACK ? 1.0f : 0.6f;
            float attackBarracks = playerState == PlayerState.ATTACK ? 1.0f : 0.65f;
            float attackRefineries = playerState == PlayerState.ATTACK ? 1.0f : 0.55f;
            float attackWorkers = playerState == PlayerState.ATTACK ? 1.0f : 0.70f;
            float attackSoldiers = playerState == PlayerState.ATTACK ? 1.0f : 0.75f;
            float attackArchers = playerState == PlayerState.ATTACK ? 1.0f : 0.75f;


            // If there is less than one base, it is vital to build a base
            heuristics["Build Base"] = Mathf.Clamp((MAX_BASES - myBases.Count) / MAX_BASES, 0, 1) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.BASE] - 1), 0, 1);
            // Build barracks
            heuristics["Build Barracks"] = Mathf.Clamp((MAX_BARRACKS - myBarracks.Count) / MAX_BARRACKS, 0, buildBarracksValue) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.BARRACKS] - 1), 0, 1);
            // Refineries are least important, max value is less to match
            heuristics["Build Refinery"] = Mathf.Clamp((MAX_REFINERIES - myRefineries.Count) / MAX_REFINERIES, 0, buildRefineryValue) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.REFINERY] - 1), 0, 1f);
            Debug.LogWarning(Mathf.Clamp((DESIRED_WORKERS - myWorkers.Count) / DESIRED_WORKERS, 0f, trainWorkerValue) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.WORKER] - 1), 0, 1f) + " worker stuff");
            heuristics["Train Worker"] = Mathf.Clamp((DESIRED_WORKERS - myWorkers.Count) / DESIRED_WORKERS, 0, 1) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.WORKER] - 1), 0, 1f);
            heuristics["Train Soldier"] = Mathf.Clamp((DESIRED_SOLDIERS - mySoldiers.Count) / DESIRED_SOLDIERS, 0, trainSoldierValue) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.SOLDIER] - 1), 0, 1);
            // Train archers if not at the max
            heuristics["Train Archer"] = Mathf.Clamp((DESIRED_ARCHERS - myArchers.Count) / DESIRED_ARCHERS, 0, trainArcherValue) *
                Mathf.Clamp(Gold - (Constants.COST[UnitType.ARCHER] - 1), 0, 1);
            // Gather gold if it's below the desired amount. More urgent as gold gets low
            heuristics["Gather Gold"] = Mathf.Clamp((DESIRED_GOLD - Gold) / DESIRED_GOLD, 0, 1);
            // kill soldiers while there are any soldiers
            heuristics["Attack Soldiers"] = Mathf.Clamp((enemySoldiers.Count / Mathf.Max(1, enemySoldiers.Count)), 0, attackSoldiers);
            // Kill archers while there are archers to kill
            heuristics["Attack Archers"] = Mathf.Clamp(((enemyArchers.Count / Mathf.Max(1, enemyArchers.Count))), 0f, attackArchers);
            // Kill workers while there are workers to kill. Lower maximum priority than enemy troops.
            heuristics["Attack Workers"] = Mathf.Clamp(((enemyWorkers.Count / Mathf.Max(1, enemyWorkers.Count))), 0f, attackWorkers);
            // Attack enemy Bases
            heuristics["Attack Bases"] = Mathf.Clamp(((enemyBases.Count / Mathf.Max(1, enemyBases.Count))), 0f, attackBases);
            // Attack enemy Barracks
            heuristics["Attack Barracks"] = Mathf.Clamp(((enemyBarracks.Count / Mathf.Max(1, enemyBarracks.Count))), 0f, attackBarracks);
            // Attack enemy Refineries
            heuristics["Attack Refineries"] = Mathf.Clamp((enemyRefineries.Count / Mathf.Max(1, enemyRefineries.Count)), 0f, attackRefineries);
        }

        /// <summary>
        /// Gather gold at the closest mine and deliver it to the main base.
        /// </summary>
        private void GatherGold()
        {
            // For each worker
            foreach (int worker in myWorkers)
            {
                // Grab the unit we need for this function
                Unit unit = GameManager.Instance.GetUnit(worker);

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

        /// <summary>
        /// Train workers if the base is idle and not at max workers
        /// </summary>
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

        /// <summary>
        /// Train soldiers if the barracks is idle
        /// </summary>
        private void TrainSoldiers()
        {
            // For each barracks, determine if it should train a soldier or an archer
            foreach (int barracksNbr in myBarracks)
            {
                // Get the barracks
                Unit barracksUnit = GameManager.Instance.GetUnit(barracksNbr);

                // If this barracks still exists, is idle, we need soldiers, and have gold
                if (barracksUnit != null && barracksUnit.IsBuilt
                    && barracksUnit.CurrentAction == UnitAction.IDLE
                    && Gold >= Constants.COST[UnitType.SOLDIER])
                {
                    Train(barracksUnit, UnitType.SOLDIER);
                }
            }
        }

        /// <summary>
        /// Train archers if the barracks is idle
        /// </summary>
        private void TrainArchers()
        {
            foreach (int barracksNbr in myBarracks)
            {
                // Get the barracks
                Unit barracksUnit = GameManager.Instance.GetUnit(barracksNbr);

                // If this barracks still exists, is idle, we need archers, and have gold
                if (barracksUnit != null && barracksUnit.IsBuilt
                         && barracksUnit.CurrentAction == UnitAction.IDLE
                         && Gold >= Constants.COST[UnitType.ARCHER])
                {
                    Train(barracksUnit, UnitType.ARCHER);
                }
            }
        }

        #endregion

        #region Private Methods

        /// <summary>
        /// Find the mine closest to the worker
        /// </summary>
        /// <param name="workerNbr"></param>
        /// <returns></returns>
        private int FindClosestMineToWorker(int workerNbr)
        {
            int closestMineNbr = -1;
            float minDistance = float.MaxValue;

            // Get the position of the initial worker
            Vector3Int workerPosition = GameManager.Instance.GetUnit(workerNbr).GridPosition;

            // Find the closest mine
            foreach (int mineNbr in mines)
            {
                Unit mineUnit = GameManager.Instance.GetUnit(mineNbr);
                if (mineUnit != null && mineUnit.Health > 0)
                {
                    float distance = Vector3Int.Distance(workerPosition, mineUnit.GridPosition);
                    if (distance < minDistance)
                    {
                        minDistance = distance;
                        closestMineNbr = mineNbr;
                    }
                }
            }

            return closestMineNbr;
        }

        #endregion
    }
}