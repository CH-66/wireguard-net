<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建新节点"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="节点名称" prop="node_name" required>
        <el-input
          v-model="form.node_name"
          placeholder="请输入节点名称，例如：laptop-home"
          maxlength="100"
          show-word-limit
        >
          <template #prepend>
            <el-icon><Monitor /></el-icon>
          </template>
        </el-input>
        <div class="form-tip">节点的唯一标识名称，建议使用有意义的命名</div>
      </el-form-item>

      <el-form-item label="平台类型" prop="platform" required>
        <el-radio-group v-model="form.platform">
          <el-radio value="linux">
            <el-icon><Monitor /></el-icon>
            Linux
          </el-radio>
          <el-radio value="windows">
            <el-icon><Monitor /></el-icon>
            Windows
          </el-radio>
        </el-radio-group>
        <div class="form-tip">选择节点的操作系统类型</div>
      </el-form-item>

      <el-form-item label="节点描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="可选，输入节点的描述信息"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        type="primary"
        :loading="loading"
        @click="handleSubmit"
      >
        <el-icon class="mr-1"><Check /></el-icon>
        创建节点
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { Monitor, Check } from '@element-plus/icons-vue'
import { useNodesStore } from '@/stores/nodes'
import type { NodeCreateRequest } from '@/types/node'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

const nodesStore = useNodesStore()

const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const form = reactive<NodeCreateRequest>({
  node_name: '',
  platform: 'linux',
  description: ''
})

// 表单验证规则
const rules: FormRules = {
  node_name: [
    { required: true, message: '请输入节点名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  platform: [
    { required: true, message: '请选择平台类型', trigger: 'change' }
  ],
  description: [
    { max: 500, message: '长度不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 监听visible变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const success = await nodesStore.createNode(form)
        if (success) {
          emit('success')
          handleClose()
        }
      } finally {
        loading.value = false
      }
    }
  })
}

// 关闭对话框
function handleClose() {
  dialogVisible.value = false
  resetForm()
}

// 重置表单
function resetForm() {
  form.node_name = ''
  form.platform = 'linux'
  form.description = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.form-tip {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.el-radio {
  margin-right: 20px;
}
</style>
