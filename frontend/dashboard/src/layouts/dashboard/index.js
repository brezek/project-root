import { useState, useEffect } from "react";
import axios from "axios";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import ProjectsTable from "layouts/dashboard/components/Projects";
import ProjectOverview from "layouts/dashboard/components/ProjectOverview";

function Dashboard() {
  const [topProjects, setTopProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // ✅ Fetch projects on mount
  useEffect(() => {
    setIsLoading(true);
    axios
      .get("http://127.0.0.1:8000/get_top_projects")
      .then((response) => {
        const projects = response.data.projects.slice(0, 3);
        setTopProjects(projects);

        // ✅ Auto-select the most recently updated project
        if (projects.length > 0) {
          const latestProject = projects.sort(
            (a, b) => new Date(b.last_updated) - new Date(a.last_updated)
          )[0];
          setSelectedProject(latestProject);
        }
      })
      .catch((error) => console.error("Error fetching projects:", error))
      .finally(() => setIsLoading(false));
  }, []);

  // ✅ Handle project selection from the table
  const handleProjectSelect = (project) => {
    setSelectedProject(project);
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {/* 🔹 TOP 4 STATISTICS CARDS */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="weekend"
                title="Bookings"
                count={281}
                percentage={{ color: "success", amount: "+55%", label: "than last week" }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="leaderboard"
                title="Today's Users"
                count="2,300"
                percentage={{ color: "success", amount: "+3%", label: "than last month" }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="store"
                title="Revenue"
                count="34k"
                percentage={{ color: "success", amount: "+1%", label: "than yesterday" }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="primary"
                icon="person_add"
                title="Followers"
                count="+91"
                percentage={{ color: "success", amount: "", label: "Just updated" }}
              />
            </MDBox>
          </Grid>
        </Grid>

        {/* 🔹 TOP 3 PROJECT CHARTS */}
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            {!isLoading &&
              topProjects.map((project, index) => (
                <Grid key={project.id || index} item xs={12} md={6} lg={4}>
                  <MDBox mb={3}>
                    <ReportsLineChart
                      color={index === 0 ? "info" : index === 1 ? "success" : "dark"}
                      title={`Project: ${project.name}`}
                      description={project.description}
                      date={`Last updated: ${new Date(project.last_updated).toLocaleString()}`}
                      chart={{
                        labels: project.timeline || [],
                        datasets: [{ label: project.name, data: project.data || [] }],
                      }}
                    />
                  </MDBox>
                </Grid>
              ))}
          </Grid>
        </MDBox>

        {/* 🔹 PROJECTS TABLE & OVERVIEW */}
        <MDBox>
          <Grid container spacing={3}>
            {/* Left: Clickable Projects Table */}
            <Grid item xs={12} md={6} lg={8}>
              <ProjectsTable onProjectSelect={handleProjectSelect} />
            </Grid>

            {/* Right: Updates Based on Selection */}
            <Grid item xs={12} md={6} lg={4}>
              <ProjectOverview project={selectedProject} />
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
