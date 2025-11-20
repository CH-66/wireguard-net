/**
 * 表单验证工具函数
 */

/**
 * 验证端口号
 */
export function validatePort(_rule: any, value: any, callback: any): void {
  if (value === '' || value === null || value === undefined) {
    callback()
    return
  }
  
  const port = Number(value)
  if (isNaN(port) || port < 1 || port > 65535) {
    callback(new Error('端口号必须在 1-65535 之间'))
  } else {
    callback()
  }
}

/**
 * 验证IPv4地址
 */
export function validateIPv4(_rule: any, value: any, callback: any): void {
  if (value === '' || value === null || value === undefined) {
    callback()
    return
  }
  
  const ipv4Regex = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  if (!ipv4Regex.test(value)) {
    callback(new Error('请输入有效的IPv4地址'))
  } else {
    callback()
  }
}

/**
 * 验证CIDR格式
 */
export function validateCIDR(_rule: any, value: any, callback: any): void {
  if (value === '' || value === null || value === undefined) {
    callback()
    return
  }
  
  const cidrRegex = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/([0-9]|[1-2][0-9]|3[0-2])$/
  if (!cidrRegex.test(value)) {
    callback(new Error('请输入有效的CIDR格式（如：10.0.0.0/24）'))
  } else {
    callback()
  }
}

/**
 * 验证公网端点格式（IP:PORT）
 */
export function validateEndpoint(_rule: any, value: any, callback: any): void {
  if (value === '' || value === null || value === undefined) {
    callback(new Error('公网端点不能为空'))
    return
  }
  
  const parts = value.split(':')
  if (parts.length !== 2) {
    callback(new Error('格式应为 IP:PORT'))
    return
  }
  
  const [ip, port] = parts
  const ipv4Regex = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  const portNum = Number(port)
  
  if (!ipv4Regex.test(ip)) {
    callback(new Error('IP地址格式不正确'))
  } else if (isNaN(portNum) || portNum < 1 || portNum > 65535) {
    callback(new Error('端口号必须在 1-65535 之间'))
  } else {
    callback()
  }
}
