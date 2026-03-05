#!/usr/bin/env node
/**
 * VPS Integration MCP Server
 * 
 * This is an example MCP server that integrates with the VPS Integration API.
 * Use this with Poke or other MCP clients to manage your VPS.
 * 
 * Setup:
 *   1. npm install @modelcontextprotocol/sdk axios
 *   2. Set environment variables: VPS_API_URL and VPS_API_TOKEN
 *   3. Add to your MCP client configuration
 * 
 * Usage with Poke:
 *   "Hey Poke, check the system status on my VPS"
 *   "Poke, restart the nginx container"
 *   "Show me the CPU usage"
 */

const { Server } = require('@modelcontextprotocol/sdk/server');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio');
const axios = require('axios');

const API_URL = process.env.VPS_API_URL || 'http://localhost:8000';
const API_TOKEN = process.env.VPS_API_TOKEN;

if (!API_TOKEN) {
  console.error('Error: VPS_API_TOKEN environment variable is required');
  process.exit(1);
}

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { 'Authorization': `Bearer ${API_TOKEN}` }
});

const server = new Server({
  name: 'vps-integration',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {}
  }
});

// System Monitoring Tools
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      // System monitoring
      {
        name: 'get_system_info',
        description: 'Get VPS system information including hostname, platform, CPU, memory, and disk',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'get_cpu_usage',
        description: 'Get current CPU usage percentage and details',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'get_memory_usage',
        description: 'Get current memory usage statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'get_disk_usage',
        description: 'Get disk usage statistics for a path',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to check disk usage (default: /)',
              default: '/'
            }
          }
        }
      },
      
      // Docker management
      {
        name: 'list_containers',
        description: 'List all Docker containers',
        inputSchema: {
          type: 'object',
          properties: {
            all: {
              type: 'boolean',
              description: 'Include stopped containers',
              default: false
            }
          }
        }
      },
      {
        name: 'start_container',
        description: 'Start a Docker container',
        inputSchema: {
          type: 'object',
          properties: {
            container_id: {
              type: 'string',
              description: 'Container ID or name'
            }
          },
          required: ['container_id']
        }
      },
      {
        name: 'stop_container',
        description: 'Stop a Docker container',
        inputSchema: {
          type: 'object',
          properties: {
            container_id: {
              type: 'string',
              description: 'Container ID or name'
            }
          },
          required: ['container_id']
        }
      },
      {
        name: 'restart_container',
        description: 'Restart a Docker container',
        inputSchema: {
          type: 'object',
          properties: {
            container_id: {
              type: 'string',
              description: 'Container ID or name'
            }
          },
          required: ['container_id']
        }
      },
      {
        name: 'get_container_logs',
        description: 'Get logs from a Docker container',
        inputSchema: {
          type: 'object',
          properties: {
            container_id: {
              type: 'string',
              description: 'Container ID or name'
            },
            lines: {
              type: 'number',
              description: 'Number of lines to retrieve',
              default: 100
            }
          },
          required: ['container_id']
        }
      },
      
      // File operations
      {
        name: 'read_file',
        description: 'Read contents of a file',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to the file'
            }
          },
          required: ['path']
        }
      },
      {
        name: 'write_file',
        description: 'Write content to a file',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to the file'
            },
            content: {
              type: 'string',
              description: 'Content to write'
            }
          },
          required: ['path', 'content']
        }
      },
      {
        name: 'list_directory',
        description: 'List contents of a directory',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to the directory'
            }
          },
          required: ['path']
        }
      },
      
      // Process management
      {
        name: 'list_processes',
        description: 'List running processes',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              description: 'Maximum number of processes to return',
              default: 50
            }
          }
        }
      }
    ]
  };
});

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    let result;
    
    switch (name) {
      case 'get_system_info':
        result = await api.get('/system/info');
        break;
      
      case 'get_cpu_usage':
        result = await api.get('/system/cpu');
        break;
      
      case 'get_memory_usage':
        result = await api.get('/system/memory');
        break;
      
      case 'get_disk_usage':
        result = await api.get('/system/disk', {
          params: { path: args.path || '/' }
        });
        break;
      
      case 'list_containers':
        result = await api.get('/docker/containers', {
          params: { all: args.all || false }
        });
        break;
      
      case 'start_container':
        result = await api.post(`/docker/containers/${args.container_id}/start`);
        break;
      
      case 'stop_container':
        result = await api.post(`/docker/containers/${args.container_id}/stop`);
        break;
      
      case 'restart_container':
        result = await api.post(`/docker/containers/${args.container_id}/restart`);
        break;
      
      case 'get_container_logs':
        result = await api.get(`/docker/containers/${args.container_id}/logs`, {
          params: { lines: args.lines || 100 }
        });
        break;
      
      case 'read_file':
        result = await api.get('/files/read', {
          params: { path: args.path }
        });
        break;
      
      case 'write_file':
        result = await api.post('/files/write', {
          path: args.path,
          content: args.content
        });
        break;
      
      case 'list_directory':
        result = await api.get('/files/list', {
          params: { path: args.path }
        });
        break;
      
      case 'list_processes':
        result = await api.get('/processes', {
          params: { limit: args.limit || 50 }
        });
        break;
      
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result.data, null, 2)
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

// Start the server
const transport = new StdioServerTransport();
server.connect(transport);

console.error('VPS Integration MCP Server started');
