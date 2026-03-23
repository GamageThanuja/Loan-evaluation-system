'use client';

import { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Avatar,
  Tabs,
  Tab,
  Divider,
  Alert,
  IconButton,
  InputAdornment,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Person,
  Lock,
  Info,
  Save,
  PhotoCamera,
  Visibility,
  VisibilityOff,
  CheckCircle,
  Computer,
  Storage,
  Code,
  Build,
} from '@mui/icons-material';
import { useAuth } from '@/hooks/useAuth';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function SettingsPage() {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [tabValue, setTabValue] = useState(0);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Profile form state
  const [profileData, setProfileData] = useState({
    name: user?.name || 'John Doe',
    email: user?.email || 'john.doe@loanwise.com',
    phone: user?.phone || '+94 77 123 4567',
    department: 'Loan Processing',
    employeeId: 'EMP001',
  });

  // Password form state
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  // Profile picture
  const [profilePicture, setProfilePicture] = useState<string | null>(null);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  const handleProfileChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setProfileData((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handlePasswordChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setPasswordData((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleProfilePictureClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfilePicture(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveProfile = async () => {
    try {
      // TODO: Implement actual API call
      setSuccessMessage('Profile updated successfully!');
      setErrorMessage(null);
    } catch (error) {
      setErrorMessage('Failed to update profile. Please try again.');
      setSuccessMessage(null);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setErrorMessage('New passwords do not match.');
      return;
    }
    if (passwordData.newPassword.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }
    try {
      // TODO: Implement actual API call
      setSuccessMessage('Password changed successfully!');
      setErrorMessage(null);
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      setErrorMessage('Failed to change password. Please try again.');
      setSuccessMessage(null);
    }
  };

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  // App info
  const appInfo = {
    version: '1.0.0',
    buildNumber: '2025.01.09.001',
    environment: process.env.NODE_ENV || 'development',
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    lastUpdated: 'January 9, 2025',
    nodeVersion: 'v18.x',
    nextVersion: '14.x',
  };

  return (
    <Box>


      {successMessage && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}
      {errorMessage && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setErrorMessage(null)}>
          {errorMessage}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<Person />} label="Profile" iconPosition="start" />
          <Tab icon={<Lock />} label="Security" iconPosition="start" />
          <Tab icon={<Info />} label="Application" iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Profile Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {/* Profile Picture */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Profile Picture
                </Typography>
                <Box sx={{ position: 'relative', display: 'inline-block', my: 2 }}>
                  <Avatar
                    src={profilePicture || undefined}
                    sx={{
                      width: 150,
                      height: 150,
                      fontSize: '3rem',
                      bgcolor: 'primary.main',
                    }}
                  >
                    {profileData.name.charAt(0).toUpperCase()}
                  </Avatar>
                  <IconButton
                    sx={{
                      position: 'absolute',
                      bottom: 0,
                      right: 0,
                      bgcolor: 'background.paper',
                      boxShadow: 2,
                      '&:hover': { bgcolor: 'background.paper' },
                    }}
                    onClick={handleProfilePictureClick}
                  >
                    <PhotoCamera />
                  </IconButton>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={handleFileChange}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Click the camera icon to upload a new picture
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Recommended: Square image, at least 200x200 pixels
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Profile Form */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Personal Information
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Full Name"
                      value={profileData.name}
                      onChange={handleProfileChange('name')}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={profileData.email}
                      onChange={handleProfileChange('email')}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Phone Number"
                      value={profileData.phone}
                      onChange={handleProfileChange('phone')}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Department"
                      value={profileData.department}
                      onChange={handleProfileChange('department')}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Employee ID"
                      value={profileData.employeeId}
                      disabled
                      helperText="Employee ID cannot be changed"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Role"
                      value={user?.role === 'manager' ? 'Manager' : 'Loan Officer'}
                      disabled
                      helperText="Contact admin to change role"
                    />
                  </Grid>
                </Grid>
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    startIcon={<Save />}
                    onClick={handleSaveProfile}
                  >
                    Save Changes
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Security Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Change Password
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Current Password"
                      type={showPasswords.current ? 'text' : 'password'}
                      value={passwordData.currentPassword}
                      onChange={handlePasswordChange('currentPassword')}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton onClick={() => togglePasswordVisibility('current')} edge="end">
                              {showPasswords.current ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="New Password"
                      type={showPasswords.new ? 'text' : 'password'}
                      value={passwordData.newPassword}
                      onChange={handlePasswordChange('newPassword')}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton onClick={() => togglePasswordVisibility('new')} edge="end">
                              {showPasswords.new ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                      helperText="Password must be at least 8 characters"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Confirm New Password"
                      type={showPasswords.confirm ? 'text' : 'password'}
                      value={passwordData.confirmPassword}
                      onChange={handlePasswordChange('confirmPassword')}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton onClick={() => togglePasswordVisibility('confirm')} edge="end">
                              {showPasswords.confirm ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                </Grid>
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    startIcon={<Lock />}
                    onClick={handleChangePassword}
                    disabled={!passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword}
                  >
                    Change Password
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Security Status
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircle color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Password Set"
                      secondary="Your password is set and active"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircle color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Email Verified"
                      secondary={profileData.email}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircle color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Account Active"
                      secondary="Your account is in good standing"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Application Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Application Information
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Info color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Version"
                      secondary={appInfo.version}
                    />
                    <Chip label="Latest" size="small" color="success" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Build color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Build Number"
                      secondary={appInfo.buildNumber}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Code color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Environment"
                      secondary={appInfo.environment}
                    />
                    <Chip 
                      label={appInfo.environment} 
                      size="small" 
                      color={appInfo.environment === 'production' ? 'success' : 'warning'}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Storage color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Last Updated"
                      secondary={appInfo.lastUpdated}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  System Details
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Computer color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Frontend Framework"
                      secondary={`Next.js ${appInfo.nextVersion}`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Code color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Node.js Version"
                      secondary={appInfo.nodeVersion}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Storage color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="API URL"
                      secondary={appInfo.apiUrl}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  About LoanWise
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body2" color="text.secondary" paragraph>
                  LoanWise is a comprehensive loan management system designed to streamline the loan 
                  application, evaluation, and approval process. The system helps loan officers and 
                  managers efficiently process applications while maintaining accurate records of 
                  customer information, loan history, and repayment schedules.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  For support, please contact the IT department or raise a ticket through the internal 
                  support system.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
}
