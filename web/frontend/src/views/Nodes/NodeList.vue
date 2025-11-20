<template>
  <div class="page-container">
    <div class="page-header mb-3">
      <h2>节点管理</h2>
      <p class="text-secondary">管理 WireGuard 客户端节点</p>
    </div>

    <!-- 工具栏 -->
    <el-card shadow="hover" class="mb-3">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            type="primary"
            @click="showCreateDialog = true"
          >
            <el-icon class="mr-1"><Plus /></el-icon>
            新建节点
          </el-button>
          <el-button
            :loading="nodesStore.loading"
            @click="handleRefresh"
          >
            <el-icon class="mr-1"><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索节点名称..."
            clearable
            style="width: 250px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="platformFilter"
            placeholder="平台筛选"
            clearable
            style="width: 150px; margin-left: 12px;"
          >
            <el-option label="全部平台" value="" />
            <el-option label="Linux" value="linux" />
            <el-option label="Windows" value="windows" />
          </el-select>
        </div>
      </div>
    </el-card>

    <!-- 节点列表 -->
    <el-card shadow="hover">
      <el-table
        v-loading="nodesStore.loading"
        :data="filteredNodes"
        stripe
        style="width: 100%"
      >
        <el-table-column
          prop="id"
          label="ID"
          width="80"
          align="center"
        />
        
        <el-table-column
          prop="node_name"
          label="节点名称"
          min-width="150"
        >
          <template #default="{ row }">
            <el-link
              type="primary"
              @click="handleViewDetail(row.id)"
            >
              {{ row.node_name }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column
          prop="virtual_ip"
          label="虚拟 IP"
          width="130"
        >
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.virtual_ip }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column
          prop="platform"
          label="平台"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <el-tag
              :type="row.platform === 'linux' ? 'success' : 'primary'"
              size="small"
            >
              <el-icon class="mr-1"><Monitor /></el-icon>
              {{ row.platform.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          prop="public_key"
          label="公钥"
          width="200"
        >
          <template #default="{ row }">
            <span class="monospace-text">{{ truncateText(row.public_key, 16) }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="description"
          label="描述"
          min-width="150"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ row.description || '-' }}
          </template>
        </el-table-column>

        <el-table-column
          prop="created_at"
          label="创建时间"
          width="170"
        >
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column
          label="操作"
          width="280"
          fixed="right"
          align="center"
        >
          <template #default="{ row }">
            <el-button
              size="small"
              @click="handleViewDetail(row.id)"
            >
              <el-icon class="mr-1"><View /></el-icon>
              详情
            </el-button>
            <el-button
              size="small"
              type="success"
              @click="handleDownloadConfig(row.id)"
            >
              <el-icon class="mr-1"><Download /></el-icon>
              配置
            </el-button>
            <el-button
              size="small"
              type="info"
              @click="handleDownloadScript(row.id)"
            >
              <el-icon class="mr-1"><Download /></el-icon>
              脚本
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row.id, row.node_name)"
            >
              <el-icon class="mr-1"><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>

        <template #empty>
          <el-empty description="暂无节点数据">
            <el-button type="primary" @click="showCreateDialog = true">
              创建第一个节点
            </el-button>
          </el-empty>
        </template>
      </el-table>

      <div v-if="filteredNodes.length > 0" class="table-footer">
        <span class="text-secondary">共 {{ filteredNodes.length }} 个节点</span>
      </div>
    </el-card>

    <!-- 创建节点对话框 -->
    <NodeCreateDialog
      v-model:visible="showCreateDialog"
      @success="handleRefresh"
    />

    <!-- 节点详情对话框 -->
    <NodeDetailDialog
      v-model:visible="showDetailDialog"
      :node-id="selectedNodeId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Search,
  Monitor,
  View,
  Download,
  Delete
} from '@element-plus/icons-vue'
import { useNodesStore } from '@/stores/nodes'
import { downloadNodeConfig, downloadNodeScript } from '@/api/downloads'
import { formatDateTime, truncateText } from '@/utils/format'
import NodeCreateDialog from './NodeCreateDialog.vue'
import NodeDetailDialog from './NodeDetailDialog.vue'

const nodesStore = useNodesStore()

// 搜索和筛选
const searchKeyword = ref('')
const platformFilter = ref('')

// 对话框控制
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const selectedNodeId = ref<number | null>(null)

// 过滤后的节点列表
const filteredNodes = computed(() => {
  let nodes = nodesStore.nodeList

  // 平台筛选
  if (platformFilter.value) {
    nodes = nodes.filter(node => node.platform === platformFilter.value)
  }

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    nodes = nodes.filter(node =>
      node.node_name.toLowerCase().includes(keyword) ||
      node.virtual_ip.includes(keyword) ||
      (node.description && node.description.toLowerCase().includes(keyword))
    )
  }

  return nodes
})

// 刷新列表
async function handleRefresh() {
  await nodesStore.fetchNodes()
}

// 查看详情
function handleViewDetail(id: number) {
  selectedNodeId.value = id
  showDetailDialog.value = true
}

// 下载配置
async function handleDownloadConfig(id: number) {
  try {
    await downloadNodeConfig(id)
  } catch (error) {
    // 错误已在API层处理
  }
}

// 下载脚本
async function handleDownloadScript(id: number) {
  try {
    await downloadNodeScript(id)
  } catch (error) {
    // 错误已在API层处理
  }
}

// 删除节点
async function handleDelete(id: number, name: string) {
  try {
    await ElMessageBox.confirm(
      `确定要删除节点 "${name}" 吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await nodesStore.deleteNode(id)
  } catch {
    // 用户取消或删除失败
  }
}

// 页面加载时获取节点列表
onMounted(() => {
  nodesStore.fetchNodes()
})
</script>

<style scoped>
.page-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
}

.page-header .text-secondary {
  margin-top: 8px;
  font-size: 14px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.monospace-text {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

.table-footer {
  margin-top: 16px;
  text-align: right;
}

:deep(.el-table) {
  font-size: 14px;
}
</style>
