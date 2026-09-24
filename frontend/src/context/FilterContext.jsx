import React, { createContext, useContext, useState, useMemo } from 'react';

const initialFilters = {
  role: '',
  skill: '',
  location: '',
  experience_level: '',
  remote_type: '',
  employment_type: '',
  salary_min: '',
  salary_max: '',
};

const FilterContext = createContext(null);

export const FilterProvider = ({ children }) => {
  const [filters, setFilters] = useState(initialFilters);

  const setFilter = (name, value) => {
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const resetFilters = () => {
    setFilters(initialFilters);
  };

  const activeFilterCount = useMemo(() => {
    return Object.values(filters).filter((val) => val !== '' && val !== null && val !== undefined).length;
  }, [filters]);

  const value = {
    filters,
    setFilter,
    resetFilters,
    activeFilterCount,
  };

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
};

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};
