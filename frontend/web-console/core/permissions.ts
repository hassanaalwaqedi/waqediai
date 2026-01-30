/**
 * Permission and RBAC utilities
 */

export type Permission =
    | 'admin:*'
    | 'tenants:read'
    | 'tenants:write'
    | 'users:read'
    | 'users:write'
    | 'documents:read'
    | 'documents:write'
    | 'documents:delete'
    | 'knowledge:read'
    | 'knowledge:query'
    | 'audit:read'
    | 'settings:read'
    | 'settings:write';

export type Role = 'super_admin' | 'tenant_admin' | 'analyst' | 'viewer' | 'user';

/**
 * Role-Permission mapping
 */
export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
    super_admin: ['admin:*'],
    tenant_admin: [
        'users:read', 'users:write',
        'documents:read', 'documents:write', 'documents:delete',
        'knowledge:read', 'knowledge:query',
        'audit:read',
        'settings:read', 'settings:write',
    ],
    analyst: [
        'documents:read', 'documents:write',
        'knowledge:read', 'knowledge:query',
        'audit:read',
    ],
    viewer: [
        'documents:read',
        'knowledge:read', 'knowledge:query',
    ],
    user: [
        'knowledge:query',
    ],
};

/**
 * Check if user has permission
 */
export function hasPermission(userRoles: Role[], permission: Permission): boolean {
    for (const role of userRoles) {
        const permissions = ROLE_PERMISSIONS[role] || [];

        // Super admin has all permissions
        if (permissions.includes('admin:*')) {
            return true;
        }

        if (permissions.includes(permission)) {
            return true;
        }
    }
    return false;
}

/**
 * Check if user has any of the permissions
 */
export function hasAnyPermission(userRoles: Role[], permissions: Permission[]): boolean {
    return permissions.some((p) => hasPermission(userRoles, p));
}

/**
 * Route permission mapping
 */
export const ROUTE_PERMISSIONS: Record<string, Permission[]> = {
    '/dashboard': ['knowledge:read'],
    '/tenants': ['tenants:read'],
    '/users': ['users:read'],
    '/documents': ['documents:read'],
    '/knowledge': ['knowledge:read'],
    '/audit': ['audit:read'],
    '/settings': ['settings:read'],
};
