/**
 * MainLayout Component
 * Application layout with navigation and header
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Layout as AntLayout,
  Menu,
  Typography,
  Space,
  Button,
  Badge,
  Avatar,
  Dropdown,
  theme,
  Drawer,
} from 'antd';
import {
  DashboardOutlined,
  BookOutlined,
  BarChartOutlined,
  SettingOutlined,
  MenuOutlined,
  BellOutlined,
  UserOutlined,
  GithubOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import type { HealthResponse } from '../types';

const { Header, Sider, Content } = AntLayout;
const { Title, Text } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
  healthStatus?: HealthResponse | null;
}

type MenuKey = 'dashboard' | 'courses' | 'quiz' | 'analytics' | 'settings';

const MainLayout: React.FC<MainLayoutProps> = ({ children, healthStatus }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileDrawerVisible, setMobileDrawerVisible] = useState(false);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // Get current path to set selected menu item
  const getCurrentKey = (): MenuKey => {
    const path = location.pathname;
    if (path === '/' || path === '/dashboard') return 'dashboard';
    if (path === '/courses') return 'courses';
    if (path === '/quiz') return 'quiz';
    if (path === '/analytics') return 'analytics';
    if (path === '/settings') return 'settings';
    return 'dashboard';
  };

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/courses',
      icon: <BookOutlined />,
      label: 'Courses',
    },
    {
      key: '/quiz',
      icon: <QuestionCircleOutlined />,
      label: 'Quiz Generator',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      label: 'Logout',
    },
  ];

  const getHealthStatus = () => {
    if (!healthStatus) return 'checking';
    if (healthStatus.status === 'healthy') return 'healthy';
    if (healthStatus.status === 'degraded') return 'warning';
    return 'error';
  };

  const getStatusColor = () => {
    const status = getHealthStatus();
    switch (status) {
      case 'healthy':
        return '#52c41a';
      case 'warning':
        return '#faad14';
      case 'error':
        return '#ff4d4f';
      default:
        return '#d9d9d9';
    }
  };

  const handleMenuClick = (key: string) => {
    navigate(key);
    setMobileDrawerVisible(false);
  };

  const SiderMenu = () => (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[location.pathname]}
      items={menuItems}
      onClick={({ key }) => handleMenuClick(key)}
      style={{ borderRight: 0 }}
    />
  );

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {/* Desktop Sider */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        breakpoint="lg"
        collapsedWidth={0}
        onBreakpoint={(broken) => setCollapsed(broken)}
        className="desktop-sider"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div className="logo">
          <BookOutlined style={{ fontSize: 24, color: '#fff' }} />
          {!collapsed && (
            <Title level={5} style={{ margin: '0 0 0 12px', color: '#fff', whiteSpace: 'nowrap' }}>
              Open-Instruct
            </Title>
          )}
        </div>
        <SiderMenu />
      </Sider>

      {/* Mobile Drawer */}
      <Drawer
        title="Open-Instruct"
        placement="left"
        onClose={() => setMobileDrawerVisible(false)}
        open={mobileDrawerVisible}
        className="mobile-drawer"
        width={256}
      >
        <SiderMenu />
      </Drawer>

      <AntLayout style={{ marginLeft: collapsed ? 0 : 200, transition: 'all 0.2s' }}>
        <Header
          className="main-header"
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'sticky',
            top: 0,
            zIndex: 100,
          }}
        >
          <Space>
            <Button
              className="mobile-trigger"
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setMobileDrawerVisible(true)}
            />
            <Title level={4} style={{ margin: 0 }} className="header-title">
              {menuItems.find((item) => item.key === location.pathname)?.label || 'Dashboard'}
            </Title>
          </Space>

          <Space size="middle">
            <Badge color={getStatusColor()} count={healthStatus ? undefined : 0}>
              <Button
                type="text"
                icon={<QuestionCircleOutlined />}
                className="header-btn"
              >
                API {getHealthStatus()}
              </Button>
            </Badge>

            <Button
              type="text"
              icon={<BellOutlined />}
              className="header-btn"
            />

            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Space className="user-dropdown" style={{ cursor: 'pointer' }}>
                <Avatar size="small" icon={<UserOutlined />} />
                <Text>User</Text>
              </Space>
            </Dropdown>

            <Button
              type="text"
              icon={<GithubOutlined />}
              className="header-btn"
              href="https://github.com/yourusername/open-instruct"
              target="_blank"
            />
          </Space>
        </Header>

        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          {children}
        </Content>
      </AntLayout>

      <style>{`
        .logo {
          height: 64px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
        }
        .main-header {
          box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
        }
        .header-btn {
          font-size: 16px;
        }
        .desktop-sider {
          z-index: 1000;
        }
        @media (max-width: 992px) {
          .desktop-sider {
            display: none !important;
          }
          .ant-layout {
            margin-left: 0 !important;
          }
        }
      `}</style>
    </AntLayout>
  );
};

export default MainLayout;
