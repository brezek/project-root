import PropTypes from "prop-types";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import TimelineItem from "examples/Timeline/TimelineItem";

function ProjectOverview({ project }) {
  if (!project) {
    return (
      <Card sx={{ height: "100%" }}>
        <MDBox pt={3} px={3}>
          <MDTypography variant="h6" fontWeight="medium">
            Project Overview
          </MDTypography>
          <MDBox mt={0} mb={2}>
            <MDTypography variant="button" color="text" fontWeight="regular">
              Select a project to view details
            </MDTypography>
          </MDBox>
        </MDBox>
      </Card>
    );
  }

  return (
    <Card sx={{ height: "100%" }}>
      <MDBox pt={3} px={3}>
        <MDTypography variant="h6" fontWeight="medium">
          {project.name} Overview
        </MDTypography>
        <MDBox mt={0} mb={2}>
          <MDTypography variant="button" color="text" fontWeight="regular">
            <MDTypography display="inline" variant="body2" verticalAlign="middle">
              <Icon sx={{ color: ({ palette: { success } }) => success.main }}>arrow_upward</Icon>
            </MDTypography>
            &nbsp;
            <MDTypography variant="button" color="text" fontWeight="medium">
              {project.tabs?.length || 0} tabs
            </MDTypography>{" "}
            in this project
          </MDTypography>
        </MDBox>
      </MDBox>
      <MDBox p={2}>
        {/* Show recent project activities */}
        <TimelineItem
          color="success"
          icon="edit"
          title={`Last updated: ${project.updated_at || "No update info"}`} // Ensure updated_at is displayed
          dateTime={new Date(project.updated_at).toLocaleString()}
        />
        <TimelineItem
          color="info"
          icon="group"
          title="Team Members"
          dateTime={project.members?.join(", ") || "No members"}
        />
        <TimelineItem
          color="warning"
          icon="content_paste"
          title="Project Status"
          dateTime={project.status || "Active"}
        />
        <TimelineItem
          color="primary"
          icon="insights"
          title="Project Progress"
          dateTime={`${((project.tabs?.length || 0) / 10) * 100}% Complete`}
          lastItem
        />
      </MDBox>
    </Card>
  );
}

ProjectOverview.propTypes = {
  project: PropTypes.shape({
    name: PropTypes.string,
    description: PropTypes.string,
    tabs: PropTypes.array,
    members: PropTypes.array,
    updated_at: PropTypes.string,
    status: PropTypes.string,
  }),
};

export default ProjectOverview;
