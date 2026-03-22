'use client';

import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Switch,
  useTheme,
  useMediaQuery,
  Collapse,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  People,
  Assessment,
  Logout,
  PersonAdd,
  Brightness4,
  Brightness7,
  AccountBalance,
  ExpandLess,
  ExpandMore,
  Settings,
  VerifiedUser,
  RateReview,
} from '@mui/icons-material';
import { useAuth } from '@/hooks/useAuth';
import { useThemeContext } from '@/components/Providers';

const drawerWidth = 260;

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, logout, isManager } = useAuth();
  const { darkMode, toggleDarkMode } = useThemeContext();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [loansExpanded, setLoansExpanded] = useState(true);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
    handleProfileMenuClose();
  };

  const handleLoansClick = () => {
    setLoansExpanded(!loansExpanded);
  };

  const isLoansPath = pathname.startsWith('/applicant');

  const getPageTitle = (path: string) => {
    if (path === '/') return 'Dashboard';
    if (path === '/applicant/new') return 'New Applicant';
    if (path === '/applicant') return 'All Applicants';
    if (path.startsWith('/applicant/')) return 'Applicant Details';
    if (path === '/eligibility') return 'Eligibility';
    if (path === '/review') return 'Review';
    if (path === '/reports') return 'Reports';
    if (path.startsWith('/settings')) return 'Settings';
    return 'Loan Evaluation System';
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h6" noWrap component="div" fontWeight={700}>
          LoanWise
        </Typography>
      </Toolbar>
      <Divider />
      <List sx={{ flexGrow: 1 }}>
        {/* Dashboard */}
        <ListItem disablePadding>
          <ListItemButton
            selected={pathname === '/'}
            onClick={() => {
              router.push('/');
              if (isMobile) setMobileOpen(false);
            }}
            sx={{
              '&.Mui-selected': {
                bgcolor: 'primary.light',
                color: 'primary.contrastText',
                '&:hover': { bgcolor: 'primary.light' },
                '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
              },
            }}
          >
            <ListItemIcon sx={{ color: pathname === '/' ? 'inherit' : 'text.secondary' }}>
              <Dashboard />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItemButton>
        </ListItem>

        {/* Loans Section */}
        <ListItem disablePadding>
          <ListItemButton
            onClick={handleLoansClick}
            sx={{
              bgcolor: isLoansPath ? 'action.selected' : 'transparent',
            }}
          >
            <ListItemIcon sx={{ color: isLoansPath ? 'primary.main' : 'text.secondary' }}>
              <AccountBalance />
            </ListItemIcon>
            <ListItemText
              primary="Loans"
              primaryTypographyProps={{ fontWeight: isLoansPath ? 600 : 400 }}
            />
            {loansExpanded ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>
        </ListItem>

        <Collapse in={loansExpanded} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {/* New Applicant */}
            <ListItem disablePadding>
              <ListItemButton
                sx={{ pl: 4 }}
                selected={pathname === '/applicant/new'}
                onClick={() => {
                  router.push('/applicant/new');
                  if (isMobile) setMobileOpen(false);
                }}
              >
                <ListItemIcon sx={{ color: pathname === '/applicant/new' ? 'primary.main' : 'text.secondary' }}>
                  <PersonAdd fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="New Applicant" />
              </ListItemButton>
            </ListItem>

            {/* All Applicants */}
            <ListItem disablePadding>
              <ListItemButton
                sx={{ pl: 4 }}
                selected={pathname === '/applicant' || (pathname.startsWith('/applicant/') && pathname !== '/applicant/new')}
                onClick={() => {
                  router.push('/applicant');
                  if (isMobile) setMobileOpen(false);
                }}
              >
                <ListItemIcon sx={{ color: pathname === '/applicant' ? 'primary.main' : 'text.secondary' }}>
                  <People fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="All Applicants" />
              </ListItemButton>
            </ListItem>
          </List>
        </Collapse>

        {/* Eligibility - For Loan Officers */}
        <ListItem disablePadding>
          <ListItemButton
            selected={pathname === '/eligibility'}
            onClick={() => {
              router.push('/eligibility');
              if (isMobile) setMobileOpen(false);
            }}
            sx={{
              '&.Mui-selected': {
                bgcolor: 'primary.light',
                color: 'primary.contrastText',
                '&:hover': { bgcolor: 'primary.light' },
                '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
              },
            }}
          >
            <ListItemIcon sx={{ color: pathname === '/eligibility' ? 'inherit' : 'text.secondary' }}>
              <VerifiedUser />
            </ListItemIcon>
            <ListItemText primary="Eligibility" />
          </ListItemButton>
        </ListItem>

        {/* Review - For Bank Managers Only */}
        {isManager() && (
          <ListItem disablePadding>
            <ListItemButton
              selected={pathname === '/review'}
              onClick={() => {
                router.push('/review');
                if (isMobile) setMobileOpen(false);
              }}
              sx={{
                '&.Mui-selected': {
                  bgcolor: 'primary.light',
                  color: 'primary.contrastText',
                  '&:hover': { bgcolor: 'primary.light' },
                  '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
                },
              }}
            >
              <ListItemIcon sx={{ color: pathname === '/review' ? 'inherit' : 'text.secondary' }}>
                <RateReview />
              </ListItemIcon>
              <ListItemText primary="Review" />
            </ListItemButton>
          </ListItem>
        )}

        {/* Reports */}
        <ListItem disablePadding>
          <ListItemButton
            selected={pathname === '/reports'}
            onClick={() => {
              router.push('/reports');
              if (isMobile) setMobileOpen(false);
            }}
            sx={{
              '&.Mui-selected': {
                bgcolor: 'primary.light',
                color: 'primary.contrastText',
                '&:hover': { bgcolor: 'primary.light' },
                '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
              },
            }}
          >
            <ListItemIcon sx={{ color: pathname === '/reports' ? 'inherit' : 'text.secondary' }}>
              <Assessment />
            </ListItemIcon>
            <ListItemText primary="Reports" />
          </ListItemButton>
        </ListItem>

        <Divider sx={{ my: 1 }} />

        {/* Settings */}
        <ListItem disablePadding>
          <ListItemButton
            selected={pathname.startsWith('/settings')}
            onClick={() => {
              router.push('/settings');
              if (isMobile) setMobileOpen(false);
            }}
            sx={{
              '&.Mui-selected': {
                bgcolor: 'primary.light',
                color: 'primary.contrastText',
                '&:hover': { bgcolor: 'primary.light' },
                '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
              },
            }}
          >
            <ListItemIcon sx={{ color: pathname.startsWith('/settings') ? 'inherit' : 'text.secondary' }}>
              <Settings />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem>
          <ListItemIcon>
            {darkMode ? <Brightness7 /> : <Brightness4 />}
          </ListItemIcon>
          <ListItemText primary="Dark Mode" />
          <Switch
            edge="end"
            checked={darkMode}
            onChange={toggleDarkMode}
            color="primary"
          />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {getPageTitle(pathname)}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: { xs: 'none', sm: 'block' }, textAlign: 'right' }}>
              <Typography variant="body2">
                {user?.name}
              </Typography>
              <Typography variant="caption" color="inherit" sx={{ opacity: 0.8 }}>
                {user?.role === 'manager' ? 'Bank Manager' : 'Loan Officer'}
              </Typography>
            </Box>
            <IconButton onClick={handleProfileMenuOpen} size="small">
              <Avatar sx={{ width: 36, height: 36, bgcolor: 'secondary.main' }}>
                {user?.name?.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
          </Box>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem disabled>
              <Typography variant="body2">
                {user?.email}
              </Typography>
            </MenuItem>
            <MenuItem disabled>
              <Typography variant="caption" color="text.secondary">
                {user?.role === 'manager' ? 'Bank Manager' : 'Loan Officer'}
              </Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => { router.push('/settings'); handleProfileMenuClose(); }}>
              <ListItemIcon>
                <Settings fontSize="small" />
              </ListItemIcon>
              Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
