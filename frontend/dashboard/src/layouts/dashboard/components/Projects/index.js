import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import axios from "axios";
import MDBox from "components/MDBox";
import DataTable from "examples/Tables/DataTable";

function ProjectsTable({ onProjectSelect }) {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/get_projects/")
      .then((response) => {
        setProjects(response.data.projects);
        if (response.data.projects.length > 0) {
          const latestProject = response.data.projects.sort(
            (a, b) => new Date(b.updated_at) - new Date(a.updated_at)
          )[0];
          onProjectSelect(latestProject); // ✅ Automatically select the latest project
        }
      })
      .catch((error) => console.error("Error fetching projects:", error));
  }, [onProjectSelect]);

  const columns = [
    { Header: "Project Name", accessor: "name", align: "left" },
    { Header: "Members", accessor: "members", align: "center" },
    { Header: "Last Updated", accessor: "updated_at", align: "right" },
  ];

  const rows = projects.map((project) => ({
    name: (
      <span
        style={{ cursor: "pointer", color: "blue", textDecoration: "underline" }}
        onClick={() => onProjectSelect(project)}
      >
        {project.name}
      </span>
    ),
    members: project.members?.join(", ") || "N/A",
    updated_at: project.updated_at ? new Date(project.updated_at).toLocaleString() : "Invalid Date",
  }));

  return (
    <MDBox>
      <DataTable
        table={{ columns, rows }}
        isSorted={false}
        showTotalEntries={false}
        noEndBorder
        entriesPerPage={false}
      />
    </MDBox>
  );
}

ProjectsTable.propTypes = {
  onProjectSelect: PropTypes.func.isRequired, // Ensure this prop is required
};

export default ProjectsTable;
