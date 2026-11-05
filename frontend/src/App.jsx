import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import AuthPage from './pages/AuthPage';
import OverviewPage from './pages/OverviewPage';
import SitesPage from './pages/SitesPage';
import AlertsPage from './pages/AlertsPage';
import OutlookPage from './pages/OutlookPage';
import AnalyticsPage from './pages/AnalyticsPage';
import DataQualityPage from './pages/DataQualityPage';
import ModelEvaluationPage from './pages/ModelEvaluationPage';
import SettingsPage from './pages/SettingsPage';
import {
  fetchSites,
  fetchAlerts,
  fetchValidationScenarios,
  fetchCurrentUser,
  syncSiteEnvironment,
  acknowledgeAlert,
  logAlertAction,
  logoutUser,
  getAuthToken
} from './api';

export default function App() {
  const [activeView, setActiveView] = useState('overview');
  const [currentUser, setCurrentUser] = useState(null);
  const [sites, setSites] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [activeScenario, setActiveScenario] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadDataForUser = async (user) => {
    setIsLoading(true);
    try {
      const [sitesData, alertsData, scenariosData] = await Promise.all([
        fetchSites().catch(() => []),
        fetchAlerts().catch(() => []),
        fetchValidationScenarios().catch(() => [])
      ]);

      setSites(sitesData);
      setAlerts(alertsData);
      setScenarios(scenariosData);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      fetchCurrentUser()
        .then((user) => {
          if (user) {
            setCurrentUser(user);
            loadDataForUser(user);
          } else {
            setIsLoading(false);
          }
        })
        .catch(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    loadDataForUser(user);
  };

  const handleLogout = () => {
    logoutUser();
    setCurrentUser(null);
    setSites([]);
    setAlerts([]);
  };

  const handleSyncSite = async (siteId) => {
    await syncSiteEnvironment(siteId);
    const updatedSites = await fetchSites();
    setSites(updatedSites);
    const updatedAlerts = await fetchAlerts();
    setAlerts(updatedAlerts);
  };

  const handleAcknowledgeAlert = async (alertId) => {
    await acknowledgeAlert(alertId);
    const updatedAlerts = await fetchAlerts();
    setAlerts(updatedAlerts);
  };

  const handleLogAlertAction = async (alertId, actionCode, feedback) => {
    await logAlertAction(alertId, actionCode, feedback);
    const updatedAlerts = await fetchAlerts();
    setAlerts(updatedAlerts);
  };

  // If not logged in, show AuthPage
  if (!currentUser) {
    return <AuthPage onLoginSuccess={handleLoginSuccess} />;
  }

  const unacknowledgedCount = alerts.filter((a) => !a.acknowledged_at).length;

  return (
    <div className="flex min-h-screen bg-[#f7f5f1]">
      {/* Sidebar based on user image */}
      <Sidebar
        activeView={activeView}
        setActiveView={setActiveView}
        unacknowledgedAlertsCount={unacknowledgedCount}
        currentUser={currentUser}
        onOpenSettings={() => setActiveView('settings')}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          activeView={activeView}
          activeScenario={activeScenario}
          onSelectScenario={(sc) => {
            setActiveScenario(sc);
            if (sc) {
              setActiveView('model_eval');
            }
          }}
          scenarios={scenarios}
          currentUser={currentUser}
          onLogout={handleLogout}
        />

        <main className="flex-1 overflow-y-auto">
          {activeView === 'overview' && (
            <OverviewPage
              sites={sites}
              alerts={alerts}
              onSelectSite={() => setActiveView('sites')}
              onOpenValidationLab={() => setActiveView('model_eval')}
              onAcknowledgeAlert={handleAcknowledgeAlert}
              onNavigateToView={(view) => setActiveView(view)}
            />
          )}

          {activeView === 'sites' && (
            <SitesPage
              sites={sites}
              onSyncSite={handleSyncSite}
              onSelectSite={() => setActiveView('overview')}
            />
          )}

          {activeView === 'alerts' && (
            <AlertsPage
              alerts={alerts}
              onAcknowledge={handleAcknowledgeAlert}
              onLogAction={handleLogAlertAction}
            />
          )}

          {activeView === 'outlook' && <OutlookPage sites={sites} />}

          {activeView === 'analytics' && <AnalyticsPage sites={sites} />}

          {activeView === 'data_quality' && (
            <DataQualityPage onUploadSuccess={() => loadDataForUser(currentUser)} />
          )}

          {activeView === 'model_eval' && <ModelEvaluationPage />}

          {activeView === 'settings' && (
            <SettingsPage
              currentUser={currentUser}
              onUserChange={(usr) => {
                setCurrentUser(usr);
                loadDataForUser(usr);
              }}
            />
          )}
        </main>
      </div>
    </div>
  );
}
