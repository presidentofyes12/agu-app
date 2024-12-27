export const UPLOAD_API_KEY="bcb4c4716fcdf9ca3c1fbdedb972aec6"
export const RPC_URL="wss://pulsechain-rpc.publicnode.com"

export const contractAddress = '0x5959769b4353344fA783843C5b2A3211de700f64'
export  const contractABI = [
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			}
		],
		"name": "DataMarkedAsStale",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "metadata",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "DataRegistered",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "content",
				"type": "string"
			}
		],
		"name": "DataRetrieved",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			},
			{
				"indexed": false,
				"internalType": "bool",
				"name": "isVerified",
				"type": "bool"
			}
		],
		"name": "DataVerified",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			},
			{
				"internalType": "uint256",
				"name": "threshold",
				"type": "uint256"
			}
		],
		"name": "markDataAsStale",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "metadata",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "content",
				"type": "string"
			}
		],
		"name": "registerData",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			},
			{
				"internalType": "string",
				"name": "newMetadata",
				"type": "string"
			}
		],
		"name": "updateMetadata",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "dataPointers",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			},
			{
				"internalType": "string",
				"name": "metadata",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			}
		],
		"name": "getMetadata",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getRegisteredIdentifiers",
		"outputs": [
			{
				"internalType": "bytes32[]",
				"name": "",
				"type": "bytes32[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "offChainData",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			},
			{
				"internalType": "string",
				"name": "content",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			}
		],
		"name": "retrieveData",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "userData",
		"outputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "identifier",
				"type": "bytes32"
			}
		],
		"name": "verifyData",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]; // Your contract ABI
export const votingPeriod= 1440
export const permVotingPeriod= 525949
export const plateformProposalKey="affba9d46a77d7816291608ee948c0e755a3314477bd3a9495aa3c9ba2139b06"
export const PROPOSAL_TYPES = {
	all:'All',
	active: 'Active',
	expired: 'Expired'
}
export const proposalTypes = [
  {
    name: 'Strategic Proposal',
    purpose:
      'Outlining strategic objectives and goals for an organization or initiative',
    approach:
      'Analyzing current environment, identifying challenges and opportunities, proposing solutions aligned with objectives',
    outcome: 'A strategic roadmap with clear action steps for implementation',
  },
  {
    name: 'Resource Proposal',
    purpose:
      'Requesting resources (financial, human, or material) to achieve a specific objective',
    approach:
      'Justifying the need for resources, outlining allocation and utilization, demonstrating return on investment',
    outcome:
      'An allocation plan detailing resource use and a strategy for maximizing impact',
  },
  {
    name: 'Innovation Proposal',
    purpose:
      'Introducing new ideas, technologies, or methodologies to address a challenge',
    approach:
      'Presenting innovative concepts with clear explanation of potential impact and feasibility',
    outcome:
      'A well-defined implementation plan for the innovative solution, outlining steps to realize it',
  },
  {
    name: 'Impact Proposal',
    purpose: 'Addressing specific societal, environmental, or economic impact',
    approach:
      'Assessing current situation, identifying root causes, presenting evidence-based interventions',
    outcome:
      'Measurable impact metrics tracking progress and a framework for evaluating effectiveness',
  },
  {
    name: 'Collaboration Proposal',
    purpose: 'Seeking partnerships or collaborations with other organizations',
    approach:
      'Identifying organizations with complementary strengths and interests, outlining potential benefits for each collaborator',
    outcome:
      'A well-defined collaboration framework with roles, responsibilities, and communication channels',
  },
  {
    name: 'Development Proposal',
    purpose:
      'Proposing a new development project or initiative for positive change',
    approach:
      'Defining project scope, objectives, deliverables, outlining project management plan, identifying stakeholders',
    outcome:
      'A comprehensive development plan with clear milestones and a timeline for completion',
  },
  {
    name: 'Policy Proposal',
    purpose: 'Advocating for policy changes or reforms to address an issue',
    approach:
      'Analyzing policy issue, impact on stakeholders, proposing specific legislative solutions with supporting evidence',
    outcome:
      'Clearly defined policy recommendations and a comprehensive advocacy strategy',
  },
  {
    name: 'Capacity Building Proposal',
    purpose:
      'Strengthening capacity of an organization, community, or individual',
    approach:
      'Assessing capabilities and resources, identifying areas for improvement, proposing capacity-building activities',
    outcome:
      'A capacity-building plan addressing weaknesses and a long-term sustainability strategy',
  },
  {
    name: 'Quality Improvement Proposal',
    purpose: 'Enhancing quality of a product, service, or process',
    approach:
      'Identifying areas needing improvement, analyzing root causes, proposing solutions and improvement measures',
    outcome:
      'A quality improvement plan with metrics for tracking progress and ongoing evaluation',
  },
  {
    name: 'Communication Proposal',
    purpose:
      "Improving an organization's or initiative's stakeholder communication",
    approach:
      'Assessing communication needs and methods, identifying target audiences and channels, proposing effective solutions',
    outcome:
      'A comprehensive communication plan outlining strategies to enhance engagement',
  },
  {
    name: 'Evaluation Proposal',
    purpose:
      'Conducting a rigorous evaluation of a program, project, or initiative',
    approach:
      'Designing evaluation methodology with data collection techniques, KPIs, and timeline',
    outcome:
      'A thorough evaluation report with findings, recommendations, and an action plan',
  },
  {
    name: 'Training and Development Proposal',
    purpose:
      'Providing training and professional development to improve skills and knowledge',
    approach:
      'Identifying training needs, designing curriculum, outlining delivery plan',
    outcome:
      'A well-defined training program with clear learning objectives, delivery plan, and evaluation',
  },
];

// Marketplace event kinds
export const MARKETPLACE_EVENT_KINDS = {
  STALL_CREATE: 30017,
  PRODUCT_CREATE: 30018,
  ORDER_CREATE: 30019,
  PAYMENT_REQUEST: 30020,
  ORDER_STATUS_UPDATE: 30021,
};

// Marketplace-related constants
export const MARKETPLACE_CONSTANTS = {
  MAX_PRODUCTS_PER_STALL: 100,
  MAX_IMAGES_PER_PRODUCT: 5,
  MAX_SPECS_PER_PRODUCT: 10,
};