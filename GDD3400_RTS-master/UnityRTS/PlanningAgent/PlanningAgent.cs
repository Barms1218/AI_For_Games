using System.Collections.Generic;
using System.Linq;
using GameManager.EnumTypes;
using GameManager.GameElements;
using UnityEngine;
using System;
using static UnityEngine.UI.GridLayoutGroup;
using System.Xml.Serialization;
using System.Net.Mail;
using UnityEngine.Experimental.UIElements;

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
        /// <summary>
        /// Do three hills for each value, when your score starts to 
        /// decrease after the third hill you're done.
        /// </summary>
        /// 

        private float DESIRED_WORKERS = 30f;
        private float MAX_BASES = 1.8f;
        private float MAX_BARRACKS = 4;
        private float MAX_REFINERIES = 0.75f;
        private float DESIRED_SOLDIERS = 20.5f;
        private float DESIRED_ARCHERS = 35;
        private float DESIRED_GOLD = 2000;

        private const int WORKER_OFFSET = 5;
        private const int BASE_OFFSET = 2;
        private const int BARRACKS_OFFSET = 3;
        private const int REFINERY_OFFSEET = 1;
        private const int SOLDIER_OFFSET = 15;
        private const int ARCHER_OFFSET = 12;

        // How much to change the semi-constants by.
        private float SEMI_CONSTANT_OFFSET = 5f;

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
        /// A list of all the enemis
        /// </summary>
        private List<int> totalEnemies { get; set; }

        /// <summary>
        /// The amount of the enemy's gold
        /// </summary>
        private float enemyGold { get; set; }

        /// <summary>
        /// List of the possible build positions for a 3x3 unit
        /// </summary>
        private List<Vector3Int> buildPositions { get; set; }

        /// <summary>
        /// The values that will help the agent make decisions
        /// </summary>
        private Dictionary<String, float> heuristics;

        /// <summary>
        /// The values that will contribute to learning between
        /// rounds.
        /// </summary>
        private Dictionary<float, float> learningValues;

        /// <summary>
        /// Keep track of the peak values for each 
        /// of my learning values, per round.
        /// </summary>
        private Dictionary<String, float> myStats;

        /// <summary>
        /// Keep track of the enemy's peak numbers
        /// such as maximum soldiers, workers, etc.
        /// </summary>
        private Dictionary<String, float> enemyStats;

        /// <summary>
        /// The state that the player's forces are in.
        /// </summary>
        private PlayerState playerState;

        /// <summary>
        /// The total score of all values compared between
        /// player agent and enemy agent.
        /// </summary>
        private float totalScore;

        /// <summary>
        /// Check to see how things look to the elft
        /// </summary>
        private bool exploringLeft;

        /// <summary>
        /// Check to see how things look to the right
        /// </summary>
        private bool exploringRight;

        private int currentConstIndex;

        private int maxHills = 3;

        private int currentHill = 0;

        private int changeDirection = 1;

        private bool doneExploring = false;

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
                if (enemyWorkers.Count > 0)
                {
                    buildPositions = buildPositions.OrderBy(pos => Vector3Int.Distance(pos, GameManager.Instance.GetUnit(mainMineNbr).GridPosition)).ToList();
                }

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
        public void AttackEnemy(string value, List<int> mySoldiers, List<int> myArchers)
        {

            // For each of my troops in this collection
            foreach (int troopNbr in mySoldiers)
            {
                List<int> enemies = new List<int>();

                // If this troop is idle, give him something to attack
                Unit troopUnit = GameManager.Instance.GetUnit(troopNbr);

                if (troopUnit.CurrentAction == UnitAction.IDLE && enemies.Count > 0)
                {
                    switch(value)
                    {
                        case "Attack Soldier":
                            enemies = enemySoldiers;
                            //AttackEnemy(mySoldiers, enemySoldiers);
                            //AttackEnemy(myArchers, enemySoldiers);
                            break;
                        case "Attack Archer":
                            enemies = enemyArchers;
                            //AttackEnemy(mySoldiers, enemyArchers);
                            //AttackEnemy(myArchers, enemyArchers);
                            break;
                        case "Attack Worker":
                            enemies = enemyWorkers;
                            //AttackEnemy(mySoldiers, enemyWorkers);
                            //AttackEnemy(myArchers, enemyWorkers);
                            break;
                        case "Attack Base":
                            enemies = enemyBases;
                            //AttackEnemy(mySoldiers, enemyBases);
                            //AttackEnemy(myArchers, enemyBases);
                            break;
                        case "Attack Barracks":
                            enemies = enemyBarracks;
                            //AttackEnemy(mySoldiers, enemyBarracks);
                            //AttackEnemy(myArchers, enemyBarracks);
                            break;
                        case "Attack Refinery":
                            enemies = enemyRefineries;
                            //AttackEnemy(mySoldiers, enemyRefineries);
                            //AttackEnemy(myArchers, enemyRefineries);
                            break;
                    }
                    Attack(troopUnit, GameManager.Instance.GetUnit(enemies[UnityEngine.Random.Range(0, enemies.Count)]));
                }
            }
            // For each of my troops in this collection
            foreach (int troopNbr in myArchers)
            {
                List<int> enemies = new List<int>();

                // If this troop is idle, give him something to attack
                Unit troopUnit = GameManager.Instance.GetUnit(troopNbr);

                if (troopUnit.CurrentAction == UnitAction.IDLE && enemies.Count > 0)
                {
                    switch (value)
                    {
                        case "Attack Soldier":
                            enemies = enemySoldiers;
                            //AttackEnemy(mySoldiers, enemySoldiers);
                            //AttackEnemy(myArchers, enemySoldiers);
                            break;
                        case "Attack Archer":
                            enemies = enemyArchers;
                            //AttackEnemy(mySoldiers, enemyArchers);
                            //AttackEnemy(myArchers, enemyArchers);
                            break;
                        case "Attack Worker":
                            enemies = enemyWorkers;
                            //AttackEnemy(mySoldiers, enemyWorkers);
                            //AttackEnemy(myArchers, enemyWorkers);
                            break;
                        case "Attack Base":
                            enemies = enemyBases;
                            //AttackEnemy(mySoldiers, enemyBases);
                            //AttackEnemy(myArchers, enemyBases);
                            break;
                        case "Attack Barracks":
                            enemies = enemyBarracks;
                            //AttackEnemy(mySoldiers, enemyBarracks);
                            //AttackEnemy(myArchers, enemyBarracks);
                            break;
                        case "Attack Refinery":
                            enemies = enemyRefineries;
                            //AttackEnemy(mySoldiers, enemyRefineries);
                            //AttackEnemy(myArchers, enemyRefineries);
                            break;
                    }
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

            switch (currentConstIndex)
            {
                case 0:
                    HillClimb(0.5f, ref DESIRED_WORKERS, WORKER_OFFSET);
                    Log("Workers Value : " + DESIRED_WORKERS.ToString());
                    break;
                case 1:
                    HillClimb(0.2f, ref MAX_BASES, BASE_OFFSET);
                    Log("Base Value: " + MAX_BASES.ToString());
                    break;
                case 2:
                    HillClimb(1f, ref MAX_BARRACKS, BARRACKS_OFFSET);
                    Log("Barracks Value: " + MAX_BARRACKS.ToString());
                    break;
                case 3:
                    HillClimb(0.25f, ref MAX_REFINERIES, REFINERY_OFFSEET);
                    Log("Refinery Value: " + MAX_REFINERIES.ToString());
                    break;
                case 4:
                    HillClimb(0.5f, ref DESIRED_SOLDIERS, SOLDIER_OFFSET);
                    Log("Soldier Value: " + DESIRED_SOLDIERS.ToString());
                    break;
                case 5:
                    HillClimb(0.4f, ref DESIRED_ARCHERS, ARCHER_OFFSET);
                    Log("Archer Value" + DESIRED_ARCHERS.ToString());
                    break;
            }

            Debug.Log("PlanningAgent::Learn");

            Log("Total Score was: " + totalScore.ToString());

        }

        /// <summary>
        /// Called before each match between two agents.  Matches have
        /// multiple rounds. 
        /// </summary>
        public override void InitializeMatch()
        {
            Debug.Log("PlanningAgent::InitializeMatch");
        }

        /// <summary>
        /// Called at the beginning of each round in a match.
        /// There are multiple rounds in a single match between two agents.
        /// </summary>
        public override void InitializeRound()
        {
            // Reset the round timer
            totalScore = 0f;

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
                {"Attack", 0f },
                {"Attack Archers", 0f },
                {"Attack Soldiers", 0f },
                {"Attack Workers", 0f },
                {"Attack Bases", 0f },
                {"Attack Barracks", 0f },
                {"Attack Refineries", 0f }
            };

            // Initialize the learning values dictionary
            learningValues = new Dictionary<float, float>()
            {
                {DESIRED_WORKERS, 0f },
                {DESIRED_SOLDIERS, 0f },
                {DESIRED_ARCHERS, 0f },
                {MAX_BARRACKS, 0f },
                {MAX_BASES, 0f },
                {MAX_REFINERIES, 0f }
            };

            // Re-Initialize enemy stats for the round
            enemyStats = new Dictionary<String, float>()
            {
                {"Soldier Count", 0 },
                {"Archer Count", 0 },
                {"Worker Count", 0 },
                {"Base Count", 0 },
                {"Barracks Count", 0 },
                {"Refinery Count", 0 }
            };

            // Re-Initialize my stats for the round 
            myStats = new Dictionary<String, float>()
            {
                {"Soldier Count", 0 },
                {"Archer Count", 0 },
                {"Worker Count", 0 },
                {"Base Count", 0 },
                {"Barracks Count", 0 },
                {"Refinery Count", 0 }
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
                enemyGold = GameManager.Instance.GetAgent(enemyAgentNbr).Gold;
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
                mainMineNbr = FindClosestMineToWorker(enemyWorkers[0]);
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


            foreach (KeyValuePair<String, float> item in heuristics)
            {
                if (item.Value > 0.25f)
                {
                    Debug.LogWarning("ACTION: " + item + " AND ITS VALUE IS: " + item.Value);
                    Debug.LogWarning(((DESIRED_WORKERS - myWorkers.Count) / DESIRED_WORKERS));
                    DoThing(item.Key);
                    AttackEnemy(item.Key, mySoldiers, myArchers);
                }
            }

            if (enemyWorkers.Count + enemyBases.Count > 0)
            {
                TrackEnemyValues();
            }
            if (myWorkers.Count + myBases.Count > 0)
            {
                TrackAgentValues();
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
            }
        }

        /// <summary>
        /// How the actions are calculated
        /// State-Based calculations done as part of the heuristics calculations
        /// </summary>
        private void CalculateHeuristics()
        {
            // State-Based Values. Gold and Bases not included because those are top priority always.
            float trainWorkerValue = 1f;
            float trainSoldierValue = playerState == PlayerState.BuildArmy ? 1.0f : 0.7f;
            float trainArcherValue = playerState == PlayerState.BuildArmy ? 1.0f : 0.6f;
            float buildBarracksValue = playerState == PlayerState.BuildBase || playerState == PlayerState.BuildArmy ? 1.0f : 0.75f;
            float buildRefineryValue = playerState == PlayerState.BuildBase || playerState == PlayerState.ATTACK ? 1.0f : 0.5f;
            float attackBases = playerState == PlayerState.ATTACK ? 1.0f : 0.6f;
            float attackBarracks = playerState == PlayerState.ATTACK ? 1.0f : 0.65f;
            float attackRefineries = playerState == PlayerState.ATTACK ? 1.0f : 0.55f;
            float attackWorkers = playerState == PlayerState.ATTACK ? 1.0f : 0.70f;
            float attackSoldiers = playerState == PlayerState.ATTACK ? 1.0f : 0.75f;
            float attackArchers = playerState == PlayerState.ATTACK ? 1.0f : 1.0f;


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
                    //Unit mineUnit = GameManager.Instance.GetUnit(FindClosestMineToWorker(worker));
                    Unit mineUnit = GameManager.Instance.GetUnit(mainMineNbr);
                    Unit baseUnit = GameManager.Instance.GetUnit(FindClosestBaseToWorker(worker));
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

        /// <summary>
        /// Find the mine closest to the worker
        /// </summary>
        /// <param name="workerNbr"></param>
        /// <returns></returns>
        private int FindClosestBaseToWorker(int workerNbr)
        {
            int closestMineNbr = -1;
            float minDistance = float.MaxValue;

            // Get the position of the initial worker
            Vector3Int workerPosition = GameManager.Instance.GetUnit(workerNbr).GridPosition;

            // Find the closest mine
            foreach (int baseNbr in myBases)
            {
                Unit baseUnit = GameManager.Instance.GetUnit(baseNbr);
                if (baseUnit != null && baseUnit.Health > 0)
                {
                    float distance = Vector3Int.Distance(workerPosition, baseUnit.GridPosition);
                    if (distance < minDistance)
                    {
                        minDistance = distance;
                        closestMineNbr = baseNbr;
                    }
                }
            }

            return closestMineNbr;
        }

        /// <summary>
        /// Keep track of the highest value that I get to in the round.
        /// </summary>
        private void TrackAgentValues()
        {
            if (myWorkers.Count > myStats["Worker Count"])
            {
                myStats["Worker Count"] = myWorkers.Count;
            }
            if (mySoldiers.Count > myStats["Soldier Count"])
            {
                myStats["Soldier Count"] = mySoldiers.Count;
            }
            if (myArchers.Count > myStats["Archer Count"])
            {
                myStats["Archer Count"] = myArchers.Count;
            }
            if (myBases.Count > myStats["Base Count"])
            {
                myStats["Base Count"] = myBases.Count;
            }
            if (myBarracks.Count > myStats["Barracks Count"])
            {
                myStats["Barracks Count"] = myBarracks.Count;
            }
            if (myRefineries.Count > myStats["Refinery Count"])
            {
                myStats["Refinery Count"] = myRefineries.Count;
            }
        }

        /// <summary>
        /// Keep track of the enemy's values for comparison
        /// </summary>
        private void TrackEnemyValues()
        {
            if (enemyWorkers.Count > enemyStats["Worker Count"])
            {
                Debug.LogWarning(enemyWorkers.Count);
                enemyStats["Worker Count"] = enemyWorkers.Count;
            }
            if (enemySoldiers.Count > enemyStats["Soldier Count"])
            {
                enemyStats["Soldier Count"] = enemySoldiers.Count;
            }
            if (enemyArchers.Count > enemyStats["Archer Count"])
            {
                enemyStats["Archer Count"] = enemyArchers.Count;
            }
            if (enemyBases.Count > enemyStats["Base Count"])
            {
                enemyStats["Base Count"] = enemyBases.Count;
            }
            if (enemyBarracks.Count > enemyStats["Barracks Count"])
            {
                enemyStats["Barracks Count"] = enemyBarracks.Count;
            }
            if (enemyRefineries.Count > enemyStats["Refinery Count"])
            {
                enemyStats["Refinery Count"] = enemyRefineries.Count;
            }
        }

        /// <summary>
        /// Run calculations to provide value for match
        /// </summary>
        /// <returns></returns>
        private float CalculateLearningValues()
        {
            // Get the values of my leftover units from their peak
            float myWorkerValue = myStats["Worker Count"] - myWorkers.Count;
            float mySoldierValue = myStats["Soldier Count"] - mySoldiers.Count;
            float myArcherValue = myStats["Archer Count"] - myArchers.Count;
            float myBaseValue = myStats["Base Count"] - myBases.Count;
            float myBarracksValue = myStats["Barracks Count"] - myBarracks.Count;
            float myRefineryValue = myStats["Refinery Count"] - myRefineries.Count;

            // Get the values from the enemy's leftover units from their peak
            float enemyWorkerValue = enemyStats["Worker Count"] - enemyWorkers.Count;
            float enemySoldierValue = enemyStats["Soldier Count"] - enemySoldiers.Count;
            float enemyArcherValue = enemyStats["Archer Count"] - enemyArchers.Count;
            float enemyBaseValue = enemyStats["Base Count"] - enemyBases.Count;
            float enemyBarracksValue = enemyStats["Barracks Count"] - enemyBarracks.Count;
            float enemyRefineryValue = enemyStats["Refinery Count"] - enemyRefineries.Count;

            // Add up all the values
            learningValues[0] = Mathf.Abs(enemySoldierValue - mySoldierValue);
            learningValues[1] = Mathf.Abs(enemyArcherValue - myArcherValue);
            learningValues[2] = Mathf.Abs(enemyWorkerValue - myWorkerValue);
            learningValues[3] = Mathf.Abs(enemyBaseValue - myBaseValue);
            learningValues[4] = Mathf.Abs(enemyBarracksValue - myBarracksValue);
            learningValues[5] = Mathf.Abs(enemyRefineryValue - myRefineryValue);

            foreach (float score in learningValues.Values)
            {
                totalScore += score;
            }

            // Correct game score for how long or short the round was
            totalScore /= GameManager.Instance.TotalGameTime;

            return totalScore;
        }

        /// <summary>
        /// Explore left or explore right, then
        /// begin the process of hill climbing
        /// </summary>
        /// <param name="factorChange"></param>
        /// <param name="learningValue"></param>
        private void HillClimb(float factorChange, ref float learningValue, float offSetValue)
        {
            float previousScore = totalScore;
            float newScore = CalculateLearningValues();

            // If the change made the score worse, change directions.
            if (newScore < previousScore)
            {
                changeDirection = -changeDirection;
            }

            // Make the agent explore left first
            if (!exploringLeft && !exploringRight && !doneExploring)
            {
                changeDirection = -changeDirection;
                learningValue += factorChange * changeDirection;
                exploringLeft = true;
            }
            // Make the agent explore to the right
            else if (exploringLeft)
            {
                learningValue += factorChange * 2;
                exploringRight = true;
                exploringLeft = false;
            }
            // The agent has explored both directions and is now done
            // exploring
            else if (exploringRight)
            {
                // If exploring right did worse
                if (newScore < previousScore)
                {
                    changeDirection = -changeDirection;
                }
                else
                {
                    changeDirection = 1;
                }

                exploringRight = false;
                doneExploring = true;
            }
            // Begin climbing in the direction that did better
            else
            {
                // find new hill meaning add offset to semi-constant
                if (newScore < previousScore && (currentHill < maxHills) || totalScore == 0)
                {
                    // Move to the next hill
                    currentHill++;

                    // If learning value is about to go below 0,
                    // reset the process because nothing of value will be learned.
                    if (learningValue - offSetValue < 0)
                    {
                        // The hill is not worth anything if it results in negative values
                        learningValue = 0;

                        // Change direction so that value will increase
                        changeDirection *= -1;

                        // Don't do anything more with this hill because it isn't of any value
                        return;
                    }

                    // Update value by its offset when looking for a new hill
                    learningValue += offSetValue * changeDirection;
                }
                else if (newScore < previousScore && (currentHill == maxHills))
                {
                    currentHill = 0;

                    // change constant
                    currentConstIndex++;

                    // Reset these values so every semi-constant can explore
                    exploringLeft = false;
                    exploringRight = false;
                    doneExploring = false;

                    if (currentConstIndex == 5)
                    {
                        currentConstIndex = 0;
                    }
                }
                else
                {
                    learningValue += factorChange * changeDirection;
                }
            }
        }

        #endregion
    }
}