using System.Collections.Generic;
using System.Linq;
using GameManager.EnumTypes;
using GameManager.GameElements;
using UnityEngine;
using System;
using static UnityEngine.UI.GridLayoutGroup;

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
        private const int MAX_NBR_WORKERS = 20;

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

        private Unit myBase;

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
        /// 
        /// </summary>
        public void BuildBase()
        {
            // For each worker
            foreach (int worker in myWorkers)
            {
                buildPositions = buildPositions.OrderBy(pos => Vector3Int.Distance(pos, GameManager.Instance.GetUnit(mainMineNbr).GridPosition)).ToList();
                // Grab the unit we need for this function
                Unit unit = GameManager.Instance.GetUnit(worker);

                mainBaseNbr = 0;

                // Make sure this unit actually exists and we have enough gold
                if (unit != null && Gold >= Constants.COST[UnitType.BASE]) 
                {
                    // Find the closest build position to this worker's position (DUMB) and 
                    // build the base there
                    foreach (Vector3Int toBuild in buildPositions)
                    {
                        if (GameManager.Instance.IsBoundedAreaBuildable(UnitType.BASE, toBuild))
                        {
                            Build(unit, toBuild, UnitType.BASE);
                            return;
                        }
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

                buildPositions = buildPositions.OrderBy(pos => Vector3Int.Distance(pos, GameManager.Instance.GetUnit(mainBaseNbr).GridPosition)).ToList();

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
                    if (enemySoldiers.Count > 0)
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemySoldiers[UnityEngine.Random.Range(0, enemySoldiers.Count)]));
                    }
                    // If there are archers to attack and no soldiers
                    else if (enemyArchers.Count > 0 && enemySoldiers.Count <= 0)
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyArchers[UnityEngine.Random.Range(0, enemyArchers.Count)]));
                    }
                    // If there are workers to attack
                    else if (enemyWorkers.Count > 0 && enemyArchers.Count + enemySoldiers.Count + enemyBarracks.Count <= 0)
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyWorkers[UnityEngine.Random.Range(0, enemyWorkers.Count)]));
                    }
                    // If there are barracks to attack
                    else if (enemyBarracks.Count > 0 && enemySoldiers.Count + enemyArchers.Count <= 0)
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyBarracks[UnityEngine.Random.Range(0, enemyBarracks.Count)]));
                    }
                    // If there are bases to attack
                    else if (enemyBases.Count > 0 && enemyBarracks.Count <= 0)
                    {
                        Attack(troopUnit, GameManager.Instance.GetUnit(enemyBases[UnityEngine.Random.Range(0, enemyBases.Count)]));
                    }
                    // If there are refineries to attack
                    else if (enemyRefineries.Count > 0 && enemyBases.Count + enemyBarracks.Count <= 0)
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
            playerState = PlayerState.BuildBase;
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

                    // If we don't have a base, build a base
                    if (myBases.Count < 1)
                    {
                        mainBaseNbr = -1;

                        BuildBase();
                    }

                    // If we don't have any barracks, build a barracks,
                    // but build a base first
                    if (myBarracks.Count == 0 && GameManager.Instance.GetUnit(mainBaseNbr).IsBuilt)
                    {
                        BuildBuilding(UnitType.BARRACKS);
                    }
                    
                    // If we don't have any refineries, build a refinery
                    if (myRefineries.Count == 0 && GameManager.Instance.GetUnit(mainBaseNbr).IsBuilt)
                    {
                        BuildBuilding(UnitType.REFINERY);
                    }

                    if (myRefineries.Count > 0 && myBarracks.Count > 0)
                    {
                        Debug.Log("CHANGING PLAYER STATE TO BUILD ARMY!!!!");
                        playerState = PlayerState.BuildArmy;
                    }

                    TrainWorkers(10);
                    break;
                case PlayerState.BuildArmy:

                    // Build a second barracks so my army grows faster
                    if (myBarracks.Count < 2)
                    {
                        BuildBuilding(UnitType.BARRACKS);
                    }
                    TrainSoldiers();
                    if (mySoldiers.Count + myArchers.Count > 7)
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
                    TrainWorkers(10);

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

        private void TrainWorkers(int numWorkers)
        {
            foreach (int baseNbr in myBases)
            {
                // Get the base unit
                Unit baseUnit = GameManager.Instance.GetUnit(baseNbr);

                // If the base exists, is idle, we need a worker, and we have gold
                if (baseUnit != null && baseUnit.IsBuilt
                                     && baseUnit.CurrentAction == UnitAction.IDLE
                                     && Gold >= Constants.COST[UnitType.WORKER]
                                     && myWorkers.Count < numWorkers)
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

                // If this barracks still exists, is idle, we need archers, and have gold
                if (barracksUnit != null && barracksUnit.IsBuilt
                         && barracksUnit.CurrentAction == UnitAction.IDLE
                         && Gold >= Constants.COST[UnitType.ARCHER]
                         && soldierChance <= 60)
                {
                    Train(barracksUnit, UnitType.ARCHER);
                }
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