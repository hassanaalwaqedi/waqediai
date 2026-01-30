/**
 * RBAC Hook
 * 
 * Provides permission checking for UI components.
 */

'use client';

import { useMemo, useCallback } from 'react';
import { useAuth } from './useAuth';
import {
    hasPermission,
    hasAnyPermission,
    Permission,
    Role,
    ROLE_PERMISSIONS,
} from '@/core/permissions';

export interface UseRBACReturn {
    /**
     * Check if user has specific permission
     */
    can: (permission: Permission) => boolean;

    /**
     * Check if user has any of the permissions
     */
    canAny: (permissions: Permission[]) => boolean;

    /**
     * Check if user has all of the permissions
     */
    canAll: (permissions: Permission[]) => boolean;

    /**
     * User's roles
     */
    roles: Role[];

    /**
     * Is super admin
     */
    isAdmin: boolean;

    /**
     * Is tenant admin or higher
     */
    isTenantAdmin: boolean;

    /**
     * Can manage users
     */
    canManageUsers: boolean;

    /**
     * Can manage documents
     */
    canManageDocuments: boolean;

    /**
     * Can view audit logs
     */
    canViewAudit: boolean;
}

export function useRBAC(): UseRBACReturn {
    const { user } = useAuth();

    const roles = useMemo<Role[]>(() => {
        if (!user?.roles) return [];
        return user.roles as Role[];
    }, [user]);

    const can = useCallback(
        (permission: Permission): boolean => {
            return hasPermission(roles, permission);
        },
        [roles]
    );

    const canAny = useCallback(
        (permissions: Permission[]): boolean => {
            return hasAnyPermission(roles, permissions);
        },
        [roles]
    );

    const canAll = useCallback(
        (permissions: Permission[]): boolean => {
            return permissions.every((p) => hasPermission(roles, p));
        },
        [roles]
    );

    const isAdmin = useMemo(() => roles.includes('super_admin'), [roles]);

    const isTenantAdmin = useMemo(
        () => roles.includes('super_admin') || roles.includes('tenant_admin'),
        [roles]
    );

    const canManageUsers = useMemo(
        () => can('users:write') || isAdmin,
        [can, isAdmin]
    );

    const canManageDocuments = useMemo(
        () => can('documents:write') || isAdmin,
        [can, isAdmin]
    );

    const canViewAudit = useMemo(
        () => can('audit:read') || isAdmin,
        [can, isAdmin]
    );

    return {
        can,
        canAny,
        canAll,
        roles,
        isAdmin,
        isTenantAdmin,
        canManageUsers,
        canManageDocuments,
        canViewAudit,
    };
}

/**
 * Component wrapper for permission-based rendering
 */
export function RequirePermission({
    permission,
    children,
    fallback = null,
}: {
    permission: Permission;
    children: React.ReactNode;
    fallback?: React.ReactNode;
}) {
    const { can } = useRBAC();

    if (!can(permission)) {
        return <>{ fallback } </>;
    }

    return <>{ children } </>;
}

/**
 * Component wrapper for role-based rendering
 */
export function RequireRole({
    roles: requiredRoles,
    children,
    fallback = null,
}: {
    roles: Role[];
    children: React.ReactNode;
    fallback?: React.ReactNode;
}) {
    const { roles: userRoles, isAdmin } = useRBAC();

    if (isAdmin) {
        return <>{ children } </>;
    }

    const hasRole = requiredRoles.some((r) => userRoles.includes(r));
    if (!hasRole) {
        return <>{ fallback } </>;
    }

    return <>{ children } </>;
}
